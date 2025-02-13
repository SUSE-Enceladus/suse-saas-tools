import logging
from unittest.mock import (
    patch, MagicMock, call
)
from pytest import fixture

from botocore.exceptions import ClientError
from resolve_customer.error import error_record
from resolve_customer.defaults import Defaults
from resolve_customer.datazone import AWSDataZone

role_config = Defaults.get_assume_role_config('../data/assume_role.yml')


class TestAWSDataZone:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @patch('boto3.client')
    @patch('resolve_customer.datazone.Defaults.get_assume_role_config')
    @patch('resolve_customer.datazone.AWSAssumeRole')
    def setup_method(
        self, cls, mock_AWSAssumeRole, mock_get_assume_role_config,
        mock_boto_client
    ):
        mock_get_assume_role_config.return_value = role_config
        assume_role = MagicMock()
        mock_AWSAssumeRole.return_value = assume_role
        self.marketplace = mock_boto_client.return_value
        self.marketplace.get_subscription.return_value = {
            'createdAt': 'datestring',
            'createdBy': 'string',
            'domainId': 'string',
            'id': 'string',
            'retainPermissions': True,
            'status': 'APPROVED',
            'subscribedListing': {
                'description': 'string',
                'id': 'string',
                'item': {
                    'assetListing': {
                        'assetScope': {
                            'assetId': 'string',
                            'errorMessage': 'string',
                            'filterIds': [
                                'string',
                            ],
                            'status': 'string'
                        },
                        'entityId': 'string',
                        'entityRevision': 'string',
                        'entityType': 'string',
                        'forms': 'string',
                        'glossaryTerms': [
                            {
                                'name': 'string',
                                'shortDescription': 'string'
                            },
                        ]
                    },
                    'productListing': {
                        'assetListings': [
                            {
                                'entityId': 'string',
                                'entityRevision': 'string',
                                'entityType': 'string'
                            },
                        ],
                        'description': 'string',
                        'entityId': 'string',
                        'entityRevision': 'string',
                        'glossaryTerms': [
                            {
                                'name': 'string',
                                'shortDescription': 'string'
                            },
                        ],
                        'name': 'string'
                    }
                },
                'name': 'string',
                'ownerProjectId': 'string',
                'ownerProjectName': 'string',
                'revision': 'string'
            },
            'subscribedPrincipal': {
                'project': {
                    'id': 'string',
                    'name': 'string'
                }
            },
            'subscriptionRequestId': 'string',
            'updatedAt': 'datestring',
            'updatedBy': 'string'
        }
        self.subscription = AWSDataZone('domain_id', 'subscription_id')
        mock_boto_client.assert_called_once_with(
            'datazone',
            region_name='eu-central-1',
            aws_access_key_id=assume_role.get_access_key.return_value,
            aws_secret_access_key=assume_role.get_secret_access_key.return_value,
            aws_session_token=assume_role.get_session_token.return_value
        )

    @patch('boto3.client')
    @patch('resolve_customer.datazone.Defaults.get_assume_role_config')
    @patch('resolve_customer.datazone.AWSAssumeRole')
    def test_setup_incomplete(
        self, mock_AWSAssumeRole, mock_get_assume_role_config,
        mock_boto_client
    ):
        with self._caplog.at_level(logging.INFO):
            AWSDataZone('', '')
            assert 'no domain_id/subscription_id and/or role' in self._caplog.text

    @patch('boto3.client')
    @patch('resolve_customer.datazone.Defaults.get_assume_role_config')
    @patch('resolve_customer.datazone.AWSAssumeRole')
    @patch('resolve_customer.datazone.log_error')
    def test_setup_boto_client_raises(
        self, mock_log_error, mock_AWSAssumeRole,
        mock_get_assume_role_config, mock_boto_client
    ):
        mock_get_assume_role_config.return_value = role_config
        mock_boto_client.side_effect = ClientError(
            operation_name=MagicMock(),
            error_response=error_record(
                400, 'datazone client failed'
            )
        )
        with self._caplog.at_level(logging.ERROR):
            AWSDataZone('domain_id', 'subscription_id')
        assert mock_log_error.call_args_list == [
            call(
                {
                    'ResponseMetadata': {
                        'HTTPStatusCode': 400
                    },
                    'Error': {
                        'Message': 'datazone client failed',
                        'Code': 'App.Error.Unknown'
                    }
                }
            ),
            call(
                {
                    'ResponseMetadata': {
                        'HTTPStatusCode': 400
                    },
                    'Error': {
                        'Message': 'datazone client failed',
                        'Code': 'App.Error.Unknown'
                    }
                }
            )
        ]

    def test_get_subscription(self):
        assert self.subscription.get_subscription().get(
            'retainPermissions'
        ) is True
