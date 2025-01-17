#!/usr/bin/python3
from sqs_event_manager.app import lambda_handler as sqs_event_manager_lambda


def lambda_handler(event, context):
    return sqs_event_manager_lambda(event, context)
