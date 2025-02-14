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
Lambda to handle SQS messages from from
AWS Metering/Entitlement Marketplace API's
"""
import json
import logging

import requests

from sqs_event_manager.defaults import Defaults
from sqs_event_manager.queue import delete_message
from sqs_event_manager.message import AWSSNSMessage
from resolve_customer.entitlements import AWSCustomerEntitlement
from resolve_customer.error import (
    error_record, error_response
)
from typing import (
    Dict, Union
)

logger = logging.getLogger('sqs_event_manager')
logger.setLevel('INFO')

# Topic name for this lambda
topic = 'SubscriptionEvent'


def lambda_handler(event, context):
    """
    Expects event type matching the SNS topic

    Example SNS raw message

    {
        "action": "entitlement-updated",
        "customer-identifier": "Some",
        "product-code": "Some"
    }

    Example SQS event

    {
        'Records': [
            {
                'message_id': 'str',
                'receipt_handle': 'str',
                'body': json.dumps({
                    'Type' : 'str',
                    'MessageId : 'str',
                    'TopicArn' : 'str',
                    'Message' : 'SNS raw message quoted text',
                    'Timestamp' : 'str',
                    'SignatureVersion' : 'str',
                    'Signature' : 'str',
                    'SigningCertURL' : 'str',
                    'UnsubscribeURL' : 'str'
                }),
                'attributes': {
                    'ApproximateReceiveCount': 'str',
                    'SentTimestamp': 'str',
                    'SenderId': 'str',
                    'ApproximateFirstReceiveTimestamp': 'str'
                },
                'messageAttributes': {},
                'md5OfBody': 'str',
                'eventSource': 'aws:sqs',
                'eventSourceARN': 'arn:aws:sqs:us-east-1:111122223333:my-queue',
                'awsRegion': 'us-east-1'
            }
        ]
    }
    """
    try:
        logger.info(f'EVENT: {event}')
        logger.info(f'CONTEXT: {context}')
        sqs_batch_response = {
            'batchItemFailures': []
        }
        for message in event['Records']:
            sqs_batch_response['batchItemFailures'].append(
                process_message(message)
            )
        return json.dumps(
            {
                'isBase64Encoded': False,
                'statusCode': 200,
                'body': sqs_batch_response
            }
        )
    except Exception as error:
        return json.dumps(
            error_response(
                error_record(
                    500, f'{type(error).__name__}: {error}',
                    'InternalServiceErrorException'
                ), topic
            )
        )


def process_message(record: Dict) -> Dict[str, Union[str, bool]]:
    """
    Handle message received from SQS queue

    Ensure the message is proper format. Get the customer
    entitlements and send the information to the SCC service.
    """
    result = {
        'itemIdentifier': record.get('messageId') or 'unknown',
        'status': 'unknown',
        'error': True
    }
    try:
        message = AWSSNSMessage(record)
        if not message.action:
            result['status'] = 'No action defined in SNS message'
            logger.error(result['status'])
        elif message.action == 'entitlement-updated':
            # Notify SCC of customer entitlement change for the given product
            customer_id = message.customer_id
            product_code = message.product_code
            logger.info(
                'requesting entitlements for customer {} and product {}'.format(
                    customer_id, product_code
                )
            )
            entitlements = AWSCustomerEntitlement(
                customer_id, product_code
            )
            request_data = {
                'customerIdentifier': customer_id,
                'marketplaceIdentifier': 'AWS',
                'productCode': product_code,
                'entitlements': entitlements.get_entitlements()
            }
            sqs_event_manager_config = Defaults.get_sqs_event_manager_config()
            headers = {
                'Content-Type': 'application/json'
            }
            auth_token = sqs_event_manager_config.get('auth_token')
            if auth_token:
                headers['Authorization'] = f'Bearer {auth_token}'
            http_post_response = requests.post(
                sqs_event_manager_config['entitlement_change_url'],
                data=request_data,
                headers=headers
            )
            http_post_response.raise_for_status()
            result['status'] = format(http_post_response.status_code)
            result['error'] = False
        else:
            result['status'] = f'Action type {message.action}: not implemented'
            logger.error(result['status'])

        # Always clean up message except on failure
        delete_message(
            message.event_source_arn, message.receipt_handle
        )
    except Exception as error:
        result['status'] = f'{type(error).__name__}: {error}'
        logger.error(result['status'])
    return result
