import logging

from emora_stdm import CompositeDialogueFlow, DialogueFlow


import common.dialogflow_framework.stdm.dialogflow_extention as dialogflow_extention
import common.dialogflow_framework.utils.state as state_utils

import dialogflows.flows.memes as memes_flow
import dialogflows.flows.greeting as greeting_flow
import dialogflows.flows.repeating as repeating_flow
import dialogflows.scopes as scopes

logger = logging.getLogger(__name__)


composite_dialogflow = CompositeDialogueFlow(
    scopes.State.USR_ROOT,
    system_error_state=scopes.State.SYS_ERR,
    user_error_state=scopes.State.USR_ERR,
    initial_speaker=DialogueFlow.Speaker.USER,
)


composite_dialogflow.add_component(memes_flow.dialogflow, scopes.MEMES)
composite_dialogflow.add_component(greeting_flow.dialogflow, scopes.GREETING)
composite_dialogflow.add_component(repeating_flow.dialogflow, scopes.REPEATING)

dialogflow = composite_dialogflow.component(scopes.MAIN)
simplified_dialogflow = dialogflow_extention.DFEasyFilling(dialogflow=dialogflow)



def memes_request(ngrams, vars):
    flag = True
    flag = flag and "how are you" in state_utils.get_last_human_utterance(vars)["text"].lower()
    logger.info(f"memes_request={flag}")
    return flag


def greeting_request(ngrams, vars):
    flag = True
    flag = flag and "repeat" not in state_utils.get_last_human_utterance(vars)["text"].lower()
    logger.info(f"greeting_request={flag}")
    return flag


def repeating_request(ngrams, vars):
    flag = True
    return flag


##################################################################################################################
##################################################################################################################
# linking
##################################################################################################################
##################################################################################################################

for node in [scopes.State.USR_ROOT, scopes.State.USR_ERR]:
    simplified_dialogflow.add_user_serial_transitions(
        node,
        {
            (scopes.MEMES, memes_flow.State.USR_START): memes_request,
            (scopes.GREETING, greeting_flow.State.USR_START): greeting_request,
            (scopes.REPEATING, repeating_flow.State.USR_START): repeating_request,
        },
    )
composite_dialogflow.set_controller("SYSTEM")
composite_dialogflow._controller = simplified_dialogflow.get_dialogflow()
