import logging
from unittest.mock import (
    patch, MagicMock
)
from pytest import fixture

from botocore.exceptions import ClientError
from resolve_customer.error import error_record
from resolve_customer.entitlements import AWSCustomerEntitlement


class TestAWSCustomerEntitlement:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @patch('boto3.client')
    def setup_method(self, cls, mock_boto_client):
        self.marketplace = mock_boto_client.return_value
        self.marketplace.get_entitlements.return_value = {
            'Entitlements': [
                {
                    'CustomerIdentifier': 'id',
                    'Dimension': 'some',
                    'ExpirationDate': 'some',
                    'ProductCode': 'some',
                    'Value': {
                        'BooleanValue': True,
                        'DoubleValue': 42,
                        'IntegerValue': 42,
                        'StringValue': 'some'
                    }
                }
            ],
            'NextToken': 'some'
        }
        self.entitlements = AWSCustomerEntitlement('id', 'product')

    @patch('boto3.client')
    def test_setup_incomplete(self, mock_boto_client):
        with self._caplog.at_level(logging.INFO):
            AWSCustomerEntitlement('', '')
            assert 'no customer_id and/or product_code' in self._caplog.text

    @patch('boto3.client')
    def test_setup_boto_client_raises(self, mock_boto_client):
        mock_boto_client.side_effect = ClientError(
            operation_name=MagicMock(),
            error_response=error_record(
                400, 'marketplace-entitlement client failed'
            )
        )
        with self._caplog.at_level(logging.INFO):
            AWSCustomerEntitlement('id', 'product')
            assert 'marketplace-entitlement client failed' in self._caplog.text

    def test_get_entitlements(self):
        assert self.entitlements.get_entitlements() == [
            {
                'customerIdentifier': 'id',
                'dimension': 'some',
                'expirationDate': 'some',
                'productCode': 'some',
                'value': {
                    'booleanValue': True,
                    'doubleValue': 42,
                    'integerValue': 42,
                    'stringValue': 'some'
                }
            }
        ]
