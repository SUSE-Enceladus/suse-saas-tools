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

from sqs_event_manager.queue import delete_message
from sqs_event_manager.message import AWSSNSMessage
from resolve_customer.entitlements import AWSCustomerEntitlement

logger = logging.getLogger('sqs_event_manager')
logger.setLevel('INFO')


def lambda_handler(event, context):
    """
    Expects event type matching the SNS topic

    {
        'Records': [
            {
                'message_id': 'str',
                'receipt_handle': 'str',
                'body': {
                    'Type' : 'str',
                    'MessageId : 'str',
                    'TopicArn' : 'str',
                    'Message' : {
                        'action': 'str',
                        'customer-identifier': 'str',
                        'product-code': 'str',
                    },
                    'Timestamp' : 'str',
                    'SignatureVersion' : 'str',
                    'Signature' : 'str',
                    'SigningCertURL' : 'str',
                    'UnsubscribeURL' : 'str'
                },
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
    batch_item_failures = []
    sqs_batch_response = {}

    try:
        for message in event['Records']:
            process_message(message, batch_item_failures)
    except Exception as error:
        return json.dumps(
            error_response(500, f'{type(error).__name__}: {error}')
        )

    sqs_batch_response['batchItemFailures'] = batch_item_failures
    return json.dumps(sqs_batch_response)


def process_message(record: dict, batch_item_failures: dict):
    """
    Handle message received from SQS queue

    Ensure the message is proper format. Get the customer entitlements and
    send the information to the SCC service.
    """
    try:
        message = AWSSNSMessage(record)

        if not message.action:
            logger.info(f'Received an unknown message: {json.dumps(record)}')
        elif message.action == 'entitlement-updated':
            # Notify SCC of customer entitlement change for the given product
            entitlements = AWSCustomerEntitlement(
                message.customer_id,
                message.product_code
            )
            if entitlements.error:
                logger.error(
                    'Exception getting entitlements for customer '
                    f'{message.customer_id} and product '
                    '{message.product_code}. {entitlements.error}'
                )
                batch_item_failures.append({'itemIdentifier': message.message_id})
                return

            request = {  # noqa TODO: Cleanup noqa
                'customerIdentifier': message.customer_id,
                'marketplaceIdentifier': 'AWS',
                'productCode': message.product_code,
                'entitlements': entitlements.get_entitlements()
            }
            # TODO: Send entitlement update request with entitlement info
        else:
            logger.info(f'Received a message with an unhandled action type: {message.action}')

        # Always clean up message except on failure
        delete_message(message.event_source_arn, message.receipt_handle)
    except Exception as error:
        logger.error(f'Exception processing message {message.receipt_handle}: {error}')
        batch_item_failures.append({'itemIdentifier': message.message_id})


def error_response(status_code: int, message: str) -> dict:
    return {
        'isBase64Encoded': False,
        'statusCode': status_code,
        'body': message
    }
