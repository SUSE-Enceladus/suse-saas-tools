# Copyright (c) 2025 SUSE LLC.  All rights reserved.
#
# This file is part of suse-saas-tools
#
# suse-saas-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mash is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mash.  If not, see <http://www.gnu.org/licenses/>
#
"""
Lambda to retrieve customer information from
AWS Metering/Entitlement Marketplace API's
"""
import logging
import json
import base64
from typing import (
    Dict, Union, List
)

from resolve_customer.error import (
    error_record, error_response
)
from resolve_customer.customer import AWSCustomer
from resolve_customer.entitlements import AWSCustomerEntitlement

logger = logging.getLogger('resolve_customer')
logger.setLevel("INFO")

# Topic name for this lambda
topic = 'Registration'


def lambda_handler(event, context):
    """
    Expects event type matching the AWS API Gateway.

    Example event body:
    {
        "registrationToken": "some"
    }

    Example return:
    {
        "statusCode": 200,
        "isBase64Encoded": false,
        "body": {
            "marketplaceIdentifier": "AWS",
            "marketplaceAccountId": "CustomerAWSAccountId"
            "CustomerIdentifier": "CustomerIdentifier"
            "entitlements": [
                {
                    "customerIdentifier": "string",
                    "productCode": "string",
                    "expirationDate": 123123111231,
                    "dimension": "string",
                    "value": {
                        "booleanValue": true|false,
                        "doubleValue": 1,
                        "integerValue": 2,
                        "stringValue": "string"
                    }
                }
            ]
        }
    }
    """
    try:
        logger.info(f'EVENT: {event}')
        logger.info(f'CONTEXT: {context}')
        event_body = event['body']
        if event.get('isBase64Encoded'):
            event_body = base64.b64decode(event_body)
        event_body = json.loads(event_body)
        return json.dumps(
            process_event(event_body.get('registrationToken'))
        )
    except Exception as error:
        return json.dumps(
            error_response(
                error_record(
                    500, f'{type(error).__name__}: {error}', 'InternalServiceErrorException'
                ), topic
            )
        )


def process_event(
    token: str
) -> Dict[str, Union[str, int, Dict[str, Union[str, List]]]]:
    try:
        customer = AWSCustomer(token)
        if customer.error:
            return error_response(customer.error, topic)
        entitlements = AWSCustomerEntitlement(
            customer.get_id(), customer.get_product_code()
        )
        if entitlements.error:
            return error_response(entitlements.error, topic)
    except Exception as oops:
        # Some unexpected exception happened, report as internal
        # server error including the message we got
        return error_response(
            error_record(
                503, f'{type(oops).__name__}: {oops}', 'ServiceUnavailableException'
            ), topic
        )
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'body': {
            'marketplaceIdentifier': 'AWS',
            'marketplaceAccountId': customer.get_account_id(),
            'customerIdentifier': customer.get_id(),
            "productCode": entitlements.get_toplevel_product_code(),
            'entitlements': entitlements.get_entitlements()
        }
    }
