import logging
from unittest.mock import (
    patch, MagicMock
)
from pytest import fixture

from botocore.exceptions import ClientError
from resolve_customer.error import error_record
from resolve_customer.customer import AWSCustomer


class TestAWSCustomer:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @patch('boto3.client')
    def setup_method(self, cls, mock_boto_client):
        self.marketplace = mock_boto_client.return_value
        self.marketplace.resolve_customer.return_value = {
            'CustomerIdentifier': 'id',
            'CustomerAWSAccountId': 'account_id',
            'ProductCode': 'some'
        }
        self.customer = AWSCustomer('token')

    @patch('boto3.client')
    def test_setup_incomplete(self, mock_boto_client):
        with self._caplog.at_level(logging.INFO):
            AWSCustomer('')
            assert 'no marketplace token provided' in self._caplog.text

    @patch('boto3.client')
    def test_setup_boto_client_raises(self, mock_boto_client):
        mock_boto_client.side_effect = ClientError(
            operation_name=MagicMock(),
            error_response=error_record(
                400, 'meteringmarketplace client failed'
            )
        )
        with self._caplog.at_level(logging.INFO):
            AWSCustomer('token')
            assert 'meteringmarketplace client failed' in self._caplog.text

    def test_get_id(self):
        assert self.customer.get_id() == 'id'

    def test_get_account_id(self):
        assert self.customer.get_account_id() == 'account_id'

    def test_get_product_code(self):
        assert self.customer.get_product_code() == 'some'
