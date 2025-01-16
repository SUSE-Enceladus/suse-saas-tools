#!/usr/bin/python3
from resolve_customer.app import lambda_handler as resolve_customer_lambda


def lambda_handler(event, context):
    return resolve_customer_lambda(event, context)
