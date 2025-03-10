import logging
import json

from unittest.mock import (
    Mock, patch
)

from sqs_event_manager.defaults import Defaults
from sqs_event_manager.app import (
    lambda_handler, process_message
)
from pytest import fixture


class TestApp:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def setup_method(self, cls):
        # This record is for testing proper json input.
        # Please also see the message_test.py test code
        # which also tests messages as they are received
        # from SNS published data
        self.config = Defaults.get_sqs_event_manager_config(
            '../data/sqs_event_manager.yml'
        )
        self.subscription_notification = {
            "Type": "SubscriptionConfirmation",
            "MessageId": "123",
            "Token": "abc",
            "TopicArn": "arn:aws:sns:...",
            "Message": "You have chosen to subscribe...",
            "SubscribeURL": "some",
            "Timestamp": "2025-03-05T13:09:24.989Z",
            "SignatureVersion": "1",
            "Signature": "some",
            "SigningCertURL": "some.pem"
        }
        self.entitlement_updated = {
            "Type": "Notification",
            "MessageId": "123",
            "TopicArn": "arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XXX",
            "Message": {
                "action": "entitlement-updated",
                "customer-identifier": "abc123",
                "product-code": "7hn1uo40wt6psy10ovxyh4zzn"
            },
            "Timestamp": "2025-01-15 16:31:50",
            "SignatureVersion": "1",
            "Signature": "abc123",
            "SigningCertURL": "string",
            "UnsubscribeURL": "string"
        }
        self.subscribe_success = {
            "Type": "Notification",
            "MessageId": "123",
            "TopicArn": "arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XXX",
            "Message": {
                "action": "subscribe-success",
                "customer-identifier": "abc123",
                "product-code": "7hn1uo40wt6psy10ovxyh4zzn",
                "offer-identifier": "offer-abcexample123",
                "isFreeTrialTermPresent": "true"
            },
            "Timestamp": "2025-01-15 16:31:50",
            "SignatureVersion": "1",
            "Signature": "abc123",
            "SigningCertURL": "string",
            "UnsubscribeURL": "string"
        }
        self.unsubscribe_pending = {
            "Type": "Notification",
            "MessageId": "123",
            "TopicArn": "arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XXX",
            "Message": {
                "action": "unsubscribe-pending",
                "customer-identifier": "abc123",
                "product-code": "7hn1uo40wt6psy10ovxyh4zzn",
                "offer-identifier": "offer-abcexample123",
                "isFreeTrialTermPresent": "true"
            },
            "Timestamp": "2025-01-15 16:31:50",
            "SignatureVersion": "1",
            "Signature": "abc123",
            "SigningCertURL": "string",
            "UnsubscribeURL": "string"
        }
        self.unsubscribe_success = {
            "Type": "Notification",
            "MessageId": "123",
            "TopicArn": "arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XXX",
            "Message": {
                "action": "unsubscribe-success",
                "customer-identifier": "abc123",
                "product-code": "7hn1uo40wt6psy10ovxyh4zzn",
                "offer-identifier": "offer-abcexample123",
                "isFreeTrialTermPresent": "true"
            },
            "Timestamp": "2025-01-15 16:31:50",
            "SignatureVersion": "1",
            "Signature": "abc123",
            "SigningCertURL": "string",
            "UnsubscribeURL": "string"
        }
        self.subscribe_fail = {
            "Type": "Notification",
            "MessageId": "123",
            "TopicArn": "arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XXX",
            "Message": {
                "action": "subscribe-fail",
                "customer-identifier": "abc123",
                "product-code": "7hn1uo40wt6psy10ovxyh4zzn",
                "offer-identifier": "offer-abcexample123",
                "isFreeTrialTermPresent": "true"
            },
            "Timestamp": "2025-01-15 16:31:50",
            "SignatureVersion": "1",
            "Signature": "abc123",
            "SigningCertURL": "string",
            "UnsubscribeURL": "string"
        }
        self.record = {
            'messageId': 'c7b2c992-4f07-478e-bfb8-f577e8310550',
            'receiptHandle': 'AQEBZ...',
            'body': json.dumps(self.entitlement_updated),
            'attributes': {
                'ApproximateReceiveCount': '1',
                'SentTimestamp': '1738513550582',
                'SequenceNumber': '18891803542658543872',
                'MessageGroupId': '586474de88e09',
                'SenderId': 'AIDA3ZKWXZJCWPK4AZP3G',
                'MessageDeduplicationId': 'f78f3e796ac0abf15635b400b459bed17fb11608ae77cc95f6f850b165ef2faa',
                'ApproximateFirstReceiveTimestamp': '1738513550582'
            },
            'messageAttributes': {},
            'md5OfBody': '3f1b30bf45ba94b6a1cee5f9db39f60a',
            'eventSource': 'aws:sqs',
            'eventSourceARN': 'arn:aws:sqs:eu-central-1:12345:ms-testing.fifo',
            'awsRegion': 'eu-central-1'
        }

    def test_lambda_handler_invalid_event(self):
        assert lambda_handler(event={'some': 'some'}, context=Mock()) == \
            "{\"isBase64Encoded\": false, \"statusCode\": 500, \"body\": " \
            "{\"errors\": {\"SubscriptionEvent\": \"KeyError: 'Records'\", " \
            "\"Exception\": \"App.Error.InternalServiceErrorException\"}}}"

    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.process_message')
    def test_lambda_handler(
        self, mock_process_message, mock_AWSCustomerEntitlement
    ):
        mock_process_message.return_value = {}
        entitlements = Mock()
        mock_AWSCustomerEntitlement.return_value = entitlements

        lambda_handler(
            event={'Records': [self.record]},
            context=Mock()
        )
        mock_process_message.assert_called_once_with(
            self.record
        )

    @patch('sqs_event_manager.app.requests')
    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.delete_message')
    @patch('sqs_event_manager.app.Defaults.get_sqs_event_manager_config')
    def test_process_message_500(
        self, mock_get_sqs_event_manager_config, mock_delete_message,
        mock_AWSCustomerEntitlement, mock_requests
    ):
        response = Mock()
        response.status_code = 500
        response.text = 'some error'
        mock_requests.post.return_value = response
        record = self.record
        mock_get_sqs_event_manager_config.return_value = self.config
        entitlements = Mock()
        entitlements.error = {}
        mock_AWSCustomerEntitlement.return_value = entitlements
        assert process_message(record) == {
            'error': True,
            'itemIdentifier': 'c7b2c992-4f07-478e-bfb8-f577e8310550',
            'status': 'Event report failed with: some error'
        }

    @patch('sqs_event_manager.app.requests')
    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.delete_message')
    @patch('sqs_event_manager.app.Defaults.get_sqs_event_manager_config')
    def test_process_message_request_body_and_header(
        self, mock_get_sqs_event_manager_config, mock_delete_message,
        mock_AWSCustomerEntitlement, mock_requests
    ):
        response = Mock()
        response.status_code = 200
        response.text = 'some error'
        mock_requests.post.return_value = response
        record = self.record
        mock_get_sqs_event_manager_config.return_value = self.config
        entitlements = Mock()
        entitlements.error = {}
        mock_AWSCustomerEntitlement.return_value = entitlements
        process_message(record)
        mock_requests.post.assert_called_once_with(
            'https://inform-me-of-changes.com',
            json={
                'customerIdentifier': 'abc123',
                'marketplaceIdentifier': 'AWS',
                'productCode': '7hn1uo40wt6psy10ovxyh4zzn',
                'entitlements': entitlements.get_entitlements.return_value,
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer some'
            }
        )

    @patch('sqs_event_manager.app.requests')
    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.delete_message')
    @patch('sqs_event_manager.app.Defaults.get_sqs_event_manager_config')
    def test_process_message_unsubscribe_pending(
        self, mock_get_sqs_event_manager_config, mock_delete_message,
        mock_AWSCustomerEntitlement, mock_requests
    ):
        response = Mock()
        response.status_code = 200
        response.text = 'some error'
        mock_requests.post.return_value = response
        record = self.record
        mock_get_sqs_event_manager_config.return_value = self.config
        entitlements = Mock()
        entitlements.error = {}
        mock_AWSCustomerEntitlement.return_value = entitlements
        record['body'] = json.dumps(self.unsubscribe_pending)
        assert process_message(record) == {
            'error': False,
            'itemIdentifier': 'c7b2c992-4f07-478e-bfb8-f577e8310550',
            'status': 'Action to unsubscribe-pending not handled by SCC'
        }

    @patch('sqs_event_manager.app.requests')
    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.delete_message')
    @patch('sqs_event_manager.app.Defaults.get_sqs_event_manager_config')
    def test_process_message_handled_maintenance_events(
        self, mock_get_sqs_event_manager_config, mock_delete_message,
        mock_AWSCustomerEntitlement, mock_requests
    ):
        response = Mock()
        response.status_code = 200
        response.text = 'some error'
        mock_requests.post.return_value = response
        record = self.record
        mock_get_sqs_event_manager_config.return_value = self.config
        entitlements = Mock()
        entitlements.error = {}
        mock_AWSCustomerEntitlement.return_value = entitlements
        for action in [
            self.unsubscribe_success,
            self.subscribe_fail,
            self.subscribe_success
        ]:
            record['body'] = json.dumps(action)
            assert process_message(record) == {
                'error': False,
                'itemIdentifier': 'c7b2c992-4f07-478e-bfb8-f577e8310550',
                'status': 'Event report succeeded'
            }

    @patch('sqs_event_manager.app.Defaults.get_sqs_event_manager_config')
    def test_process_message_unknown_event_category(
        self, mock_get_sqs_event_manager_config
    ):
        record = self.record
        mock_get_sqs_event_manager_config.return_value = self.config
        record['body'] = json.dumps(self.subscription_notification)
        with self._caplog.at_level(logging.INFO):
            process_message(record)
            assert 'No action implemented for event type:' in \
                self._caplog.text

    @patch('sqs_event_manager.app.requests')
    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.delete_message')
    @patch('sqs_event_manager.app.Defaults.get_sqs_event_manager_config')
    def test_process_message_unknown_action(
        self, mock_get_sqs_event_manager_config, mock_delete_message,
        mock_AWSCustomerEntitlement, mock_requests
    ):
        response = Mock()
        response.status_code = 200
        response.text = 'some error'
        mock_requests.post.return_value = response
        record = self.record
        mock_get_sqs_event_manager_config.return_value = self.config
        entitlements = Mock()
        entitlements.error = {}
        mock_AWSCustomerEntitlement.return_value = entitlements
        record['body'] = record['body'].replace(
            'entitlement-updated', 'fake-event'
        )
        with self._caplog.at_level(logging.INFO):
            process_message(record)
            assert 'Action type fake-event: not implemented' in \
                self._caplog.text

    @patch('sqs_event_manager.app.requests')
    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.delete_message')
    @patch('sqs_event_manager.app.Defaults.get_sqs_event_manager_config')
    def test_process_message_no_event(
        self, mock_get_sqs_event_manager_config, mock_delete_message,
        mock_AWSCustomerEntitlement, mock_requests
    ):
        response = Mock()
        response.status_code = 200
        response.text = 'some error'
        mock_requests.post.return_value = response
        record = self.record
        mock_get_sqs_event_manager_config.return_value = self.config
        entitlements = Mock()
        entitlements.error = {}
        mock_AWSCustomerEntitlement.return_value = entitlements
        record['body'] = record['body'].replace('action', 'actions')
        with self._caplog.at_level(logging.INFO):
            process_message(record)
            assert 'No action defined in SNS message' in self._caplog.text

    @patch('sqs_event_manager.app.requests')
    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.delete_message')
    @patch('sqs_event_manager.app.Defaults.get_sqs_event_manager_config')
    def test_process_message_post_request_raises(
        self, mock_get_sqs_event_manager_config, mock_delete_message,
        mock_AWSCustomerEntitlement, mock_requests
    ):
        response = Mock()
        response.status_code = 200
        response.text = 'some error'
        mock_requests.post.return_value = response
        record = self.record
        mock_get_sqs_event_manager_config.return_value = self.config
        entitlements = Mock()
        entitlements.error = {}
        mock_AWSCustomerEntitlement.return_value = entitlements
        mock_requests.post.side_effect = Exception('some-error')
        with self._caplog.at_level(logging.ERROR):
            process_message(record)
            assert 'some-error' in self._caplog.text

    @patch('sqs_event_manager.app.AWSCustomerEntitlement')
    @patch('sqs_event_manager.app.Defaults.get_sqs_event_manager_config')
    @patch('sqs_event_manager.app.requests')
    def test_process_message_get_entitlements_error(
        self, mock_requests, mock_get_sqs_event_manager_config,
        mock_AWSCustomerEntitlement
    ):
        entitlements = Mock()
        entitlements.error = Mock()
        mock_AWSCustomerEntitlement.return_value = entitlements

        assert process_message(self.record) == {
            'error': True,
            'itemIdentifier': 'c7b2c992-4f07-478e-bfb8-f577e8310550',
            'status': f'AWSCustomerEntitlement failed with {entitlements.error}'
        }
        assert mock_requests.mock_requests.post.called is False
