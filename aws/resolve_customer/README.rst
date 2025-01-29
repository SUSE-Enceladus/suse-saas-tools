AWS ResolveCustomer interface
=============================

The lambda function is expected to be triggerd by an AWS API Gateway.

POST
----
Through AWS API Gateway

.. code::

    {
        "registrationToken": "someURLEncodedToken"
    }

RESPONSE
--------

.. code::

    {
        "statusCode": 200,
        "isBase64Encoded": false,
        "body": {
            "marketplaceIdentifier": "AWS",
            "marketplaceAccountId": "CustomerAWSAccountId"
            "customerIdentifier": "CustomerIdentifier"
            "entitlements": [
                {
                    "customerIdentifier": "string",
                    "productCode": "string",
                    "expirationDate": 123123111231,
                    "dimension": "string",
                    "value": {
                        "booleanValue": true|false,
                        "doubleValue": 1,
                        "integerValue": 2,
                        "stringValue": "string"
                    }
                }
            ]
        }
    }

ERROR RESPONSE
--------------

.. code::

    {
        "isBase64Encoded": false,
        "statusCode": HTTP_STATUS_CODE,
        "body": {
            "errors": {
                "Registration": "MESSAGE",
                "Exception": "AWS. or App. error code"
            }
        }
    }


Application handled exceptions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* 500: App.Error.InternalServiceErrorException
* 503: App.Error.ServiceUnavailableException
* 422: App.Error.MissingTokenException
* 400: App.Error.TokenException from
       InvalidTokenException, ExpiredTokenException, ThrottlingException, DisabledApiException
* 400: App.Error.EntitlementException from
       InvalidParameterException, ThrottlingException

Pass through exceptions:
~~~~~~~~~~~~~~~~~~~~~~~~

* HTTP_STATUS_CODE: code and exception name as it was provided by the client call
