import logging

from unittest.mock import (
    Mock, patch
)

from sqs_event_manager.app import (
    lambda_handler, process_message
)
from pytest import fixture

record = {
    'message_id': '123',
    'receipt_handle': 'abc123',
    'body': {
        'Type': 'Notification',
        'MessageId': '6f4eae69-8205-5531-84f7-f1b478aeb04',
        'TopicArn': 'arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XXX',
        'Message': {
            'action': 'entitlement-updated',
            'customer-identifier': 'abc123',
            'product-code': '7hn1uo40wt6psy10ovxyh4zzn',
        },
        'Timestamp': '2025-01-15 16:31:50',
        'SignatureVersion': '1',
        'Signature': 'signature',
        'SigningCertURL': 'https://cert.com',
        'UnsubscribeURL': 'https://unsub.com'
    },
    'attributes': {
        'ApproximateReceiveCount': '1',
        'SentTimestamp': '1545082649183',
        'SenderId': 'abc123',
        'ApproximateFirstReceiveTimestamp': '1545082649185'
    },
    'messageAttributes': {},
    'md5OfBody': 'md5hash',
    'eventSource': 'aws:sqs',
    'eventSourceARN': 'arn:aws:sqs:us-east-1:111122223333:my-queue',
    'awsRegion': 'us-east-1'
}


class TestApp:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def test_lambda_handler_invalid_event(self):
        assert lambda_handler(event={'some': 'some'}, context=Mock()) == \
            '{\"isBase64Encoded\": false, \"statusCode\": 500, ' \
            '\"body\": \"KeyError: \'Records\'\"}'

    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.process_message')
    def test_lambda_handler(
        self, mock_process_message, mock_AWSCustomerEntitlement
    ):
        mock_process_message.return_value = {}
        entitlements = Mock()
        mock_AWSCustomerEntitlement.return_value = entitlements

        lambda_handler(
            event={'Records': [record]},
            context=Mock()
        )
        mock_process_message.assert_called_once_with(
            record,
            []
        )

    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.delete_message')
    def test_process_message(
        self, mock_delete_message, mock_AWSCustomerEntitlement
    ):
        entitlements = Mock()
        mock_AWSCustomerEntitlement.return_value = entitlements

        batch_item_failures = []
        process_message(record, batch_item_failures)
        assert len(batch_item_failures) == 0

        record['body']['Message']['action'] = None
        with self._caplog.at_level(logging.INFO):
            process_message(record, batch_item_failures)
            assert 'Received an unknown message:' in self._caplog.text

        record['body']['Message']['action'] = 'fake-event'
        with self._caplog.at_level(logging.INFO):
            process_message(record, batch_item_failures)
            assert 'Received a message with an unhandled action type: fake-event' in self._caplog.text
