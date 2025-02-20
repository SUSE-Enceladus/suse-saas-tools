from pytest import fixture

from sqs_event_manager.message import AWSSNSMessage


class TestAWSSNSMessage:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def setup_method(self, cls):
        record_entitlement = {
            'messageId': 'c7b2c992-4f07-478e-bfb8-f577e8310550',
            'receiptHandle': 'AQEBZ...',
            'body': '{\
                "Type": "Notification", \
                "MessageId": "123", \
                "TopicArn": "arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XXX", \
                "Message" : "{\\n    \\"action\\": \\"entitlement-updated\\",\\n    \\"customer-identifier\\": \\" abc123\\",\\n    \\"product-code\\": \\"7hn1uo40wt6psy10ovxyh4zzn\\"\\n}",\n\
                "Timestamp": "2025-01-15 16:31:50", \
                "SignatureVersion": "1", \
                "Signature": "abc123", \
                "SigningCertURL": "string", \
                "UnsubscribeURL": "string"\
            }',
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
        record_maintenance = {
            'messageId': 'c7b2c992-4f07-478e-bfb8-f577e8310550',
            'receiptHandle': 'AQEBZ...',
            'body': '{\
                "Type": "Notification", \
                "MessageId": "123", \
                "TopicArn": "arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XXX", \
                "Message" : "{\\n    \\"action\\": \\"subscribe-success\\",\\n    \\"customer-identifier\\": \\" abc123\\",\\n    \\"product-code\\": \\"7hn1uo40wt6psy10ovxyh4zzn\\", \\"offer-identifier\\": \\"offer-abcexample123\\", \\"isFreeTrialTermPresent\\": \\"false\\"\\n}",\n\
                "Timestamp": "2025-01-15 16:31:50", \
                "SignatureVersion": "1", \
                "Signature": "abc123", \
                "SigningCertURL": "string", \
                "UnsubscribeURL": "string"\
            }',
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
        self.message = AWSSNSMessage(record_entitlement)
        self.maintenance = AWSSNSMessage(record_maintenance)

    def test_get_message_id(self):
        assert self.message.message_id == 'c7b2c992-4f07-478e-bfb8-f577e8310550'

    def test_get_customer_id(self):
        assert self.message.customer_id == 'abc123'

    def test_get_product_code(self):
        assert self.message.product_code == '7hn1uo40wt6psy10ovxyh4zzn'

    def test_get_receipt_handle(self):
        assert self.message.receipt_handle == 'AQEBZ...'

    def test_get_event_source_arn(self):
        assert self.message.event_source_arn == 'arn:aws:sqs:eu-central-1:12345:ms-testing.fifo'

    def test_get_action(self):
        assert self.message.action == 'entitlement-updated'

    def test_get_offer_id(self):
        assert self.maintenance.offer_id == 'offer-abcexample123'

    def test_get_free_trial_term_present(self):
        assert self.maintenance.free_trial_term_present == 'false'
