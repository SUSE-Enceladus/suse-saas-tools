import logging
from unittest.mock import (
    patch, MagicMock
)
from pytest import fixture

from botocore.exceptions import ClientError
from resolve_customer.error import error_record
from resolve_customer.defaults import Defaults
from resolve_customer.customer import AWSCustomer

role_config = Defaults.get_assume_role_config('../data/assume_role.yml')


class TestAWSCustomer:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @patch('boto3.client')
    @patch('resolve_customer.customer.Defaults.get_assume_role_config')
    @patch('resolve_customer.customer.AWSAssumeRole')
    def setup_method(
        self, cls, mock_AWSAssumeRole, mock_get_assume_role_config,
        mock_boto_client
    ):
        mock_get_assume_role_config.return_value = role_config
        assume_role = MagicMock()
        mock_AWSAssumeRole.return_value = assume_role
        self.marketplace = mock_boto_client.return_value
        self.marketplace.resolve_customer.return_value = {
            'CustomerIdentifier': 'id',
            'CustomerAWSAccountId': 'account_id',
            'ProductCode': 'some'
        }
        self.customer = AWSCustomer('token')
        mock_boto_client.assert_called_once_with(
            'meteringmarketplace',
            region_name='us-east-1',
            aws_access_key_id=assume_role.get_access_key.return_value,
            aws_secret_access_key=assume_role.get_secret_access_key.return_value,
            aws_session_token=assume_role.get_session_token.return_value
        )

    @patch('boto3.client')
    @patch('resolve_customer.customer.Defaults.get_assume_role_config')
    @patch('resolve_customer.customer.AWSAssumeRole')
    def test_setup_incomplete(
        self, mock_AWSAssumeRole, mock_get_assume_role_config,
        mock_boto_client
    ):
        with self._caplog.at_level(logging.INFO):
            AWSCustomer('')
            assert 'no marketplace token provided' in self._caplog.text

    @patch('boto3.client')
    @patch('resolve_customer.customer.Defaults.get_assume_role_config')
    @patch('resolve_customer.customer.AWSAssumeRole')
    def test_setup_boto_client_raises(
        self, mock_AWSAssumeRole, mock_get_assume_role_config,
        mock_boto_client
    ):
        error_response = error_record(
            400, 'meteringmarketplace client failed'
        )
        error_response['Error']['Code'] = \
            'AWS.ResolveCustomer.ExpiredTokenException'
        mock_boto_client.side_effect = ClientError(
            operation_name=MagicMock(),
            error_response=error_response
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
