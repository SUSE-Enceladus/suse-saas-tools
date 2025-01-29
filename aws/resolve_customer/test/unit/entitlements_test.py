import logging
from unittest.mock import (
    patch, MagicMock
)
from pytest import fixture

from botocore.exceptions import ClientError
from resolve_customer.error import error_record
from resolve_customer.defaults import Defaults
from resolve_customer.entitlements import AWSCustomerEntitlement

role_config = Defaults.get_assume_role_config('../data/assume_role.yml')


class TestAWSCustomerEntitlement:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @patch('boto3.client')
    @patch('resolve_customer.entitlements.Defaults.get_assume_role_config')
    @patch('resolve_customer.entitlements.AWSAssumeRole')
    def setup_method(
        self, cls, mock_AWSAssumeRole, mock_get_assume_role_config,
        mock_boto_client
    ):
        mock_get_assume_role_config.return_value = role_config
        assume_role = MagicMock()
        mock_AWSAssumeRole.return_value = assume_role
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
        mock_boto_client.assert_called_once_with(
            'marketplace-entitlement',
            region_name='us-east-1',
            aws_access_key_id=assume_role.get_access_key.return_value,
            aws_secret_access_key=assume_role.get_secret_access_key.return_value,
            aws_session_token=assume_role.get_session_token.return_value
        )

    @patch('boto3.client')
    @patch('resolve_customer.entitlements.Defaults.get_assume_role_config')
    @patch('resolve_customer.entitlements.AWSAssumeRole')
    def test_setup_incomplete(
        self, mock_AWSAssumeRole, mock_get_assume_role_config,
        mock_boto_client
    ):
        with self._caplog.at_level(logging.INFO):
            AWSCustomerEntitlement('', '')
            assert 'no customer_id and/or product_code' in self._caplog.text

    @patch('boto3.client')
    @patch('resolve_customer.entitlements.Defaults.get_assume_role_config')
    @patch('resolve_customer.entitlements.AWSAssumeRole')
    def test_setup_boto_client_raises(
        self, mock_AWSAssumeRole, mock_get_assume_role_config,
        mock_boto_client
    ):
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
                'dimension': 'some',
                'expirationDate': 'some',
                'value': {
                    'booleanValue': True,
                    'doubleValue': 42,
                    'integerValue': 42,
                    'stringValue': 'some'
                }
            }
        ]

    def test_get_toplevel_product_code(self):
        assert self.entitlements.get_toplevel_product_code() == 'some'
