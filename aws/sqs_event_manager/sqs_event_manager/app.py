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
                    'Message' : 'SNS raw message quoted json text',
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
    sqs_event_manager_config = Defaults.get_sqs_event_manager_config()
    result = {
        'itemIdentifier': record.get('messageId') or 'unknown',
        'status': 'unknown',
        'error': True
    }
    try:
        message = AWSSNSMessage(record)
        auth_token = sqs_event_manager_config.get('auth_token', '')
        endpoint_missing = 'missing_endpoint_setup'
        entitlements = AWSCustomerEntitlement(
            message.customer_id, message.product_code
        )
        if entitlements.error:
            result['status'] = \
                f'AWSCustomerEntitlement failed with {entitlements.error}'
            logger.error(result['status'])
            return result

        if not message.action:
            result['status'] = 'No action defined in SNS message'
            logger.error(result['status'])
        elif message.action == 'entitlement-updated':
            endpoint_url = sqs_event_manager_config.get(
                'entitlement_change_url', endpoint_missing
            )
            result.update(
                send_to(
                    entitlement_updated(message, entitlements),
                    endpoint_url, auth_token
                )
            )
        elif message.action == 'subscribe-success':
            endpoint_url = sqs_event_manager_config.get(
                'subscribe_success_url', endpoint_missing
            )
            result.update(
                send_to(
                    subscription_success(message, entitlements),
                    endpoint_url, auth_token
                )
            )
        elif message.action == 'unsubscribe-success':
            endpoint_url = sqs_event_manager_config.get(
                'unsubscribe_success_url', endpoint_missing
            )
            result.update(
                send_to(
                    subscription_removed(message, entitlements),
                    endpoint_url, auth_token
                )
            )
        elif message.action == 'subscribe-fail':
            endpoint_url = sqs_event_manager_config.get(
                'subscribe_fail_url', endpoint_missing
            )
            result.update(
                send_to(
                    subscription_failed(message, entitlements),
                    endpoint_url, auth_token
                )
            )
        elif message.action == 'unsubscribe-pending':
            result['status'] = f'Action to {message.action} not handled by SCC'
            result['error'] = False
        else:
            result['status'] = f'Action type {message.action}: not implemented'
            logger.error(result['status'])

        # Always clean up message from the queue except on a raise condition
        delete_message(
            message.event_source_arn, message.receipt_handle
        )
    except Exception as error:
        result['status'] = f'{type(error).__name__}: {error}'
        logger.error(result['status'])
    return result


def subscription_success(
    message: AWSSNSMessage, entitlements: AWSCustomerEntitlement
) -> Dict:
    """
    Construct request to notify about subscription successfully processed
    """
    request_data = basic_request(message, entitlements)
    request_data['offerIdentifier'] = message.offer_id
    request_data['isFreeTrialTermPresent'] = message.free_trial_term_present
    return request_data


def subscription_removed(
    message: AWSSNSMessage, entitlements: AWSCustomerEntitlement
) -> Dict:
    """
    Construct request to notify about subscription successfully removed
    """
    request_data = basic_request(message, entitlements)
    request_data['offerIdentifier'] = message.offer_id
    request_data['isFreeTrialTermPresent'] = message.free_trial_term_present
    return request_data


def subscription_failed(
    message: AWSSNSMessage, entitlements: AWSCustomerEntitlement
) -> Dict:
    """
    Construct request to notify about a failed subscription process
    """
    request_data = basic_request(message, entitlements)
    request_data['offerIdentifier'] = message.offer_id
    request_data['isFreeTrialTermPresent'] = message.free_trial_term_present
    return request_data


def entitlement_updated(
    message: AWSSNSMessage, entitlements: AWSCustomerEntitlement
) -> Dict:
    """
    Construct request to notify about customer entitlement
    change for the given product
    """
    return basic_request(message, entitlements)


def send_to(
    request_data: Dict, endpoint_url: str, auth_token: str = ''
) -> Dict:
    """
    Send POST request with notification data to given endpoint.
    The method raises an exception if the request fails
    """
    headers = {
        'Content-Type': 'application/json'
    }
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    logger.info(f'Sending POST data to {endpoint_url}: {request_data}')
    http_post_response = requests.post(
        endpoint_url, json=request_data, headers=headers
    )
    if http_post_response.status_code != 200:
        result = {
            'status': f'Event report failed with: {http_post_response.text}',
            'error': True
        }
        logger.error(result['status'])
    else:
        result = {
            'status': 'Event report succeeded',
            'error': False
        }
        logger.info(result['status'])
    return result


def basic_request(
    message: AWSSNSMessage, entitlements: AWSCustomerEntitlement
) -> Dict:
    """
    Build a basic request common to all expected events
    """
    request_data = {
        'customerIdentifier': message.customer_id,
        'marketplaceIdentifier': 'AWS',
        'productCode': message.product_code,
        'entitlements': entitlements.get_entitlements()
    }
    return request_data
