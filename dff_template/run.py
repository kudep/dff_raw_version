#!/usr/bin/env python

import logging
import time
import os
import random

from flask import Flask, request, jsonify
from healthcheck import HealthCheck
import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger


import common.dialogflow_framework.utils.dialogflow as dialogflow_utils
import common.dialogflow_framework.programy.text_preprocessing as text_utils
import dialogflows.main as main_dialogflow

ignore_logger("root")

sentry_sdk.init(os.getenv("SENTRY_DSN"))
SERVICE_NAME = os.getenv("SERVICE_NAME")
SERVICE_PORT = int(os.getenv("SERVICE_PORT"))
RANDOM_SEED = int(os.getenv("RANDOM_SEED", 2718))

logging.basicConfig(format="%(asctime)s - %(pathname)s - %(lineno)d - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)
health = HealthCheck(app, "/healthcheck")

DF = main_dialogflow.composite_dialogflow


def handler(human_utter_index, dialog, state):
    st_time = time.time()
    try:
        text = dialog["human_utterances"][-1]["text"]
        text = text_utils.clean_text(text)
        dialogflow_utils.load_into_dialogflow(DF, human_utter_index, dialog, state)
        response_text = dialogflow_utils.run_turn(DF, text)
        response_state = dialogflow_utils.get_dialog_state(DF)
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        logger.exception(exc)
        response_text = ""
        response_state = {}
    total_time = time.time() - st_time
    logger.info(f"{SERVICE_NAME} exec time = {total_time:.3f}s")
    return response_text, response_state

dialog = {"human_utterances":[], "bot_utterances":[]}
state = {}
while True:
    dialog["human_utterances"] += [{"text":input("input: ")}]
    response_text, response_state = handler(len(dialog["human_utterances"]), dialog, state)
    state.update(response_state)
    dialog["bot_utterances"] += [{"text":response_text}]
    print(f"bot: {response_text}")

