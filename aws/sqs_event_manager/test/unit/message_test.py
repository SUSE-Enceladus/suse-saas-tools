import json

from pytest import fixture

from sqs_event_manager.message import AWSSNSMessage


class TestAWSSNSMessage:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def setup_method(self, cls):
        message = json.dumps(
            {
                'action': 'entitlement-updated',
                'customer-identifier': 'abc123',
                'product-code': '7hn1uo40wt6psy10ovxyh4zzn',
            }
        )
        body = json.dumps(
            {
                'Type': 'Notification',
                'MessageId': '6f4eae69-8205-5531-84f7-f1b478aeb04',
                'TopicArn': 'arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XXX',
                'Message': message,
                'Timestamp': '2025-01-15 16:31:50',
                'SignatureVersion': '1',
                'Signature': 'signature',
                'SigningCertURL': 'https://cert.com',
                'UnsubscribeURL': 'https://unsub.com'
            }
        )
        record = {
            'messageId': '123',
            'receiptHandle': 'abc123',
            'body': body,
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
        self.message = AWSSNSMessage(record)

    def test_get_message_id(self):
        assert self.message.message_id == '123'

    def test_get_customer_id(self):
        assert self.message.customer_id == 'abc123'

    def test_get_product_code(self):
        assert self.message.product_code == '7hn1uo40wt6psy10ovxyh4zzn'

    def test_get_receipt_handle(self):
        assert self.message.receipt_handle == 'abc123'

    def test_get_event_source_arn(self):
        assert self.message.event_source_arn == 'arn:aws:sqs:us-east-1:111122223333:my-queue'

    def test_get_action(self):
        assert self.message.action == 'entitlement-updated'
