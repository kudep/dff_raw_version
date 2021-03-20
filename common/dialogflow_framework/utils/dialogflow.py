#!/usr/bin/env python

import logging
import os

import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger

import common.dialogflow_framework.stdm.cached_functions as cached_functions

ignore_logger("root")

sentry_sdk.init(os.getenv("SENTRY_DSN"))

logger = logging.getLogger(__name__)


def load_into_dialogflow(dialogflow, human_utter_index, dialog, state):
    cached_functions.clear_cache()
    dialogflow.reset()
    dialogflow_state = state.get("dialogflow_state")
    previous_human_utter_index = state.get("previous_human_utter_index", -1)
    interrupted_flag = (human_utter_index - previous_human_utter_index) != 1
    if dialogflow_state and not interrupted_flag:
        dialogflow.deserialize(dialogflow_state)
    agent = {
        "previous_human_utter_index": previous_human_utter_index,
        "human_utter_index": human_utter_index,
        "dialog": dialog,
        "shared_memory": state.get("shared_memory", {}),
        "response": {},
        "cache": {},
        "history": state.get("history", {}),
    }
    dialogflow.controller().vars()["agent"] = agent


def get_dialog_state(dialogflow):
    agent = dialogflow.controller().vars()["agent"]
    human_utter_index = agent["human_utter_index"]
    history = agent["history"]
    history[str(human_utter_index)] = dialogflow.controller().vars()["__system_state__"]
    state = {
        "shared_memory": agent["shared_memory"],
        "previous_human_utter_index": human_utter_index,
        "history": history,
    }
    del dialogflow.controller().vars()["agent"]
    state["dialogflow_state"] = dialogflow.serialize()
    logger.debug(f"state={state}")
    return state


def run_turn(dialogflow, text):
    dialogflow.user_turn(text)
    text = dialogflow.system_turn()
    return text
