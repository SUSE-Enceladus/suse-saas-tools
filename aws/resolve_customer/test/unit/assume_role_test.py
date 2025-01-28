import logging
from unittest.mock import (
    patch, MagicMock
)
from pytest import fixture
from datetime import datetime

from botocore.exceptions import ClientError
from resolve_customer.assume_role import AWSAssumeRole
from resolve_customer.error import error_record


class TestAWSAssumeRole:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @patch('boto3.client')
    def setup_method(self, cls, mock_boto_client):
        self.sts_client = mock_boto_client.return_value
        self.sts_client.assume_role.return_value = {
            'Credentials': {
                'AccessKeyId': 'accesskey',
                'SecretAccessKey': 'secretaccesskey',
                'SessionToken': 'string',
                'Expiration': format(datetime(2015, 1, 1))
            },
            'AssumedRoleUser': {
                'AssumedRoleId': 'string',
                'Arn': 'string'
            },
            'PackedPolicySize': 123,
            'SourceIdentity': 'string'
        }
        self.assume_role = AWSAssumeRole(
            'arn:aws:iam::some:role/PCTAccess'
        )

    @patch('boto3.client')
    def test_setup_boto_client_raises(self, mock_boto_client):
        error_response = error_record(
            400, 'sts client failed'
        )
        error_response['Error']['Code'] = \
            'AccessDeniedException'
        mock_boto_client.side_effect = ClientError(
            operation_name=MagicMock(),
            error_response=error_response
        )
        with self._caplog.at_level(logging.INFO):
            AWSAssumeRole('arn:aws:iam::some:role/PCTAccess')
            assert 'sts client failed' in self._caplog.text

    def test_get_access_key(self):
        assert self.assume_role.get_access_key() == 'accesskey'

    def test_get_secret_access_key(self):
        assert self.assume_role.get_secret_access_key() == 'secretaccesskey'

    def test_get_session_token(self):
        assert self.assume_role.get_session_token() == 'string'

    def test_get_expiration_date(self):
        assert self.assume_role.get_expiration_date() == '2015-01-01 00:00:00'
