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
import json
import base64
from typing import (
    Dict, Union, List
)

from resolve_customer.customer import AWSCustomer
from resolve_customer.entitlements import AWSCustomerEntitlement


def lambda_handler(event, context):
    """
    Expects event type matching the AWS API Gateway.

    Example event body:
    {
        "x-amzn-marketplace-token": "some"
    }

    Example return:
    {
        "statusCode": 200,
        "isBase64Encoded": False,
        "body": {
            "CustomerIdentifier": "id"
            "CustomerAWSAccountId": "account_id"
            "ProductCode": "product_code"
            "Entitlements": [
                {
                    "CustomerIdentifier": "id",
                    "Dimension": "some",
                    "ExpirationDate": date,
                    "ProductCode": "product_code",
                    "Value": {
                        "BooleanValue": true|false,
                        "DoubleValue": number,
                        "IntegerValue": number,
                        "StringValue": "str"
                    }
                }
            ]
        }
    }
    """
    try:
        event_body = event['body']
        if event.get('isBase64Encoded'):
            event_body = json.loads(base64.b64decode(event_body))
        return json.dumps(
            process_event(event_body.get('x-amzn-marketplace-token'))
        )
    except Exception as error:
        return json.dumps(
            error_response(500, f'{type(error).__name__}: {error}')
        )


def process_event(
    token: str
) -> Dict[str, Union[str, int, Dict[str, Union[str, List]]]]:
    customer = AWSCustomer(token)
    if customer.error:
        return error_response(400, customer.error)
    entitlements = AWSCustomerEntitlement(
        customer.get_id(), customer.get_product_code()
    )
    if entitlements.error:
        return error_response(400, entitlements.error)
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'body': {
            'CustomerIdentifier': customer.get_id(),
            'CustomerAWSAccountId': customer.get_account_id(),
            'ProductCode': customer.get_product_code(),
            'Entitlements': entitlements.get_entitlements()
        }
    }


def error_response(status_code: int, message: str):
    return {
        'isBase64Encoded': False,
        'statusCode': status_code,
        'body': message
    }
