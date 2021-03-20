# %%
import os
import logging
from enum import Enum, auto

import sentry_sdk

import common.dialogflow_framework.stdm.dialogflow_extention as dialogflow_extention
import common.dialogflow_framework.utils.state as state_utils

import dialogflows.scopes as scopes


sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))

logger = logging.getLogger(__name__)


class State(Enum):
    USR_START = auto()
    SYS_HI = auto()
    USR_WANT_NEWS = auto()

    SYS_MEMES = auto()
    SYS_NON_MEMES = auto()
    SYS_ERR = auto()
    USR_ERR = auto()


# %%

##################################################################################################################
# Init DialogFlow
##################################################################################################################


simplified_dialogflow = dialogflow_extention.DFEasyFilling(State.USR_START)

##################################################################################################################
##################################################################################################################
# Design DialogFlow.
##################################################################################################################
##################################################################################################################

def hi_request(ngrams, vars):
    flag = "how are you" in  state_utils.get_last_human_utterance(vars)["text"].lower()
    logger.info(f"exec hi_request={flag}")
    return flag


def hi_response(vars):
    logger.info("exec hi_response")
    try:
        return "memes mode: Hi! I'm good! What about are you?"
    except Exception as exc:
        logger.exception(exc)
        sentry_sdk.capture_exception(exc)
        return error_response(vars)


##################################################################################################################
# memes
##################################################################################################################


def memes_request(ngrams, vars):
    flag = True
    flag = flag and "memes" in state_utils.get_last_human_utterance(vars)["text"]
    logger.info(f"exec memes_request={flag}")
    return flag


def memes_response(vars):
    logger.info("exec memes_response")
    try:
        return "memes mode: I like memes"
    except Exception as exc:
        logger.exception(exc)
        sentry_sdk.capture_exception(exc)
        return error_response(vars)


##################################################################################################################
# non_memes
##################################################################################################################


def non_memes_request(ngrams, vars):
    flag = True
    logger.info(f"exec non_memes_request={flag}")
    return flag


def non_memes_response(vars):
    logger.info("exec non_memes_response")
    try:
        return "memes mode: Sorry, I can talk only about memes."
    except Exception as exc:
        logger.exception(exc)
        sentry_sdk.capture_exception(exc)
        return error_response(vars)



##################################################################################################################
# error
##################################################################################################################


def error_response(vars):
    logger.info("exec error_response")
    return "Sorry"


##################################################################################################################
##################################################################################################################
# linking
##################################################################################################################
##################################################################################################################


##################################################################################################################
#  START
# ######### transition State.USR_START -> State.SYS_HI if hi_request==True (request returns only bool values) ####
simplified_dialogflow.add_user_serial_transitions(
    State.USR_START,
    {
        State.SYS_HI: hi_request,
    },
)
# ######### if all *_request==False then transition State.USR_START -> State.SYS_ERR  #########
simplified_dialogflow.set_error_successor(State.USR_START, State.SYS_ERR)

##################################################################################################################
#  SYS_HI

# ######### transition State.SYS_HI -> State.USR_WANT_NEWS and return text from hi_response  #########
simplified_dialogflow.add_system_transition(State.SYS_HI, State.USR_WANT_NEWS, hi_response)

simplified_dialogflow.add_user_serial_transitions(
    State.USR_WANT_NEWS,
    {
        State.SYS_MEMES: memes_request,  # first place
        State.SYS_NON_MEMES: non_memes_request,  # second place
    },
)

simplified_dialogflow.set_error_successor(State.USR_WANT_NEWS, State.SYS_ERR)

simplified_dialogflow.add_system_transition(State.SYS_MEMES, State.USR_START, memes_response)
simplified_dialogflow.add_system_transition(State.SYS_NON_MEMES, State.USR_START, non_memes_response)

##################################################################################################################
#  SYS_ERR
# ######### We can use global transition for State.SYS_ERR #########
simplified_dialogflow.add_global_user_serial_transitions(
    {
        State.SYS_ERR: (lambda x, y: True, -1.0),
    },
)
simplified_dialogflow.add_system_transition(
    State.SYS_ERR,
    (scopes.MAIN, scopes.State.USR_ROOT),
    error_response,
)

##################################################################################################################
#  Compile and get dialogflow
##################################################################################################################
# do not foget this line
dialogflow = simplified_dialogflow.get_dialogflow()
