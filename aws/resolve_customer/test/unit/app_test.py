from unittest.mock import (
    Mock, patch
)

from resolve_customer.app import (
    lambda_handler, process_event
)


class TestApp:
    def test_lambda_handler_invalid_event(self):
        assert lambda_handler(event={'some': 'some'}, context=Mock()) == \
            '{\"isBase64Encoded\": false, \"statusCode\": 500, ' \
            '\"body\": \"KeyError: \'body\'\"}'

    @patch('resolve_customer.app.process_event')
    def test_lambda_handler(self, mock_process_event):
        mock_process_event.return_value = {}
        lambda_handler(
            event={
                'version': '2.0',
                'routeKey': 'ANY /ms-lambda-from-container',
                'rawPath': '/default/ms-lambda-from-container',
                'rawQueryString': '',
                'headers': {
                    'accept': '*/*',
                    'content-length': '31',
                    'content-type': 'application/x-www-form-urlencoded',
                    'host': 'some',
                    'user-agent': 'curl/8.0.1',
                    'x-amzn-trace-id': 'Root=xxx',
                    'x-forwarded-for': '79.201.150.192',
                    'x-forwarded-port': '443',
                    'x-forwarded-proto': 'https'
                },
                'requestContext': {
                    'accountId': '810320120389',
                    'apiId': 'jfh2r389u9',
                    'domainName': 'some',
                    'domainPrefix': 'jfh2r389u9',
                    'http': {
                        'method': 'POST',
                        'path': '/default/ms-lambda-from-container',
                        'protocol': 'HTTP/1.1',
                        'sourceIp': '79.201.150.192',
                        'userAgent': 'curl/8.0.1'
                    },
                    'requestId': 'EcDY1h1zFiAEPLQ=',
                    'routeKey': 'ANY /ms-lambda-from-container',
                    'stage': 'default',
                    'time': '15/Jan/2025:16:44:01 +0000',
                    'timeEpoch': 1736959441730
                },
                'body': 'eyJyZWdpc3RyYXRpb25Ub2tlbiI6ICJ0b2tlbiJ9Cg==',
                'isBase64Encoded': True
            },
            context=Mock()
        )
        mock_process_event.assert_called_once_with(
            'token'
        )

    @patch('resolve_customer.app.AWSCustomer')
    @patch('resolve_customer.app.AWSCustomerEntitlement')
    def test_process_event(
        self, mock_AWSCustomerEntitlement, mock_AWSCustomer
    ):
        customer = Mock()
        customer.error = ''
        entitlements = Mock()
        entitlements.error = ''
        mock_AWSCustomer.return_value = customer
        mock_AWSCustomerEntitlement.return_value = entitlements
        assert process_event('token') == {
            'isBase64Encoded': False,
            'statusCode': 200,
            'body': {
                'CustomerIdentifier': customer.get_id.return_value,
                'CustomerAWSAccountId': customer.get_account_id.return_value,
                'ProductCode': customer.get_product_code.return_value,
                'Entitlements': entitlements.get_entitlements.return_value
            }
        }
        customer.error = 'some-customer-error'
        assert process_event('token') == {
            'isBase64Encoded': False,
            'statusCode': 400,
            'body': 'some-customer-error'
        }
        customer.error = ''
        entitlements.error = 'some-entitlement-error'
        assert process_event('token') == {
            'isBase64Encoded': False,
            'statusCode': 400,
            'body': 'some-entitlement-error'
        }
