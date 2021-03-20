import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


#  vars is described in README.md


def get_shared_memory(vars):
    return vars["agent"]["shared_memory"]


def get_human_utter_index(vars):
    return vars["agent"]["human_utter_index"]


def get_previous_human_utter_index(vars):
    return vars["agent"]["previous_human_utter_index"]


def get_last_human_utterance(vars):
    return vars["agent"]["dialog"]["human_utterances"][-1]


def get_last_bot_utterance(vars):
    if vars["agent"]["dialog"]["bot_utterances"]:
        return vars["agent"]["dialog"]["bot_utterances"][-1]
    else:
        return {"text": ""}


def save_to_shared_memory(vars, **kwargs):
    vars["agent"]["shared_memory"].update(kwargs)