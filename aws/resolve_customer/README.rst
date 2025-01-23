AWS ResolveCustomer interface
=============================

The lambda function is expected to be triggerd by an AWS API Gateway.

POST
----
Through AWS API Gateway

.. code::

    {
        "registrationToken": "some"
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
            "CustomerIdentifier": "CustomerIdentifier"
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
            "errors": {"Registration": "MESSAGE"}
        }
    }

* 500: Internal Server Error
* 503: Service unavailable, any non AWS ClientException
* 422: no marketplace token provided / no customer_id and/or product_code provided
* HTTP_STATUS_CODE: HTTP status code as it was provided by the client call
