AWS ResolveCustomer API
=======================

The resolve customer interface provides customer and entitelement
information such that a company customer portal e.g. the SUSE
Customer Center (SCC) can create an account to allow product
access by a cloud marketplace registration process.

Higlevel Deployment Plan
------------------------

To deploy the resolve_customer API in the AWS cloud the
following services must be used:

* AWS Elastic Container Registry
* AWS Lambda
* AWS Api Gateway

For the deployment the following steps are needed:

1. Push the SUSE SaaS tool chain container to an AWS
   Elastic Container Registry

2. Create an AWS Lambda function from the container URL
   created in 1. The Lambda has to provide the following
   configuration settings:

   * Image -> CMD override -> app_resolve_customer.lambda_handler
   * Configuration -> Timeout 15sec

3. Edit the IAM policy for the created function at:

   .. code::

       IAM -> Policies -> AWSLambdaBasicExecutionRole-your-lambda-id

   Add a Statement similar to the following:

   .. code::

       {
           "Effect": "Allow",
           "Resource": "arn:aws:iam::123:role/Some",
           "Action": "sts:AssumeRole"
       }

   The role identified by the specified resource needs to be defined
   in an account used as the listing account for AWS marketplace, configured
   to allow the lambda function role to assume the marketplace role via
   secure token service in the trust policy. This marketplace role needs
   to provide specific permissions required by the implementation of the
   SUSE SaaS toolchain to query marketplace APIs.

4. Create an API Gateway trigger for the lambda function.
   In the simplest form an open gateway can be configured.
   However, for a production setup this will not be sufficient.
   The API Gateway must be an HTTP type and has to setup
   the following parameter mapping:

   .. code::

       API Gateway -> APIs -> your-gateway -> Integrations

   Create a new parameter mapping to manage the HTTP status code:

   .. code::

       Mapping Type: Response status code
       Response key: 200
       Parameter to modify: statuscode
       Modification type: Overwrite
       Value: $response.body.statusCode

   The parameter mapping is required such that the return code
   of the SUSE SaaS toolchain matches with the HTTP status code
   of the Gateway response

   Create a new parameter mapping to manage the content type:

   .. code::

       Mapping Type: Incoming requests
       Parameter to modify: header.content-type
       Modification type: Remove

   The API Gateway manages the content-type of the incoming request
   in different ways. Our code expects that the request to the
   AWS lambda function uses application/json which is the default
   setting of the gateway. To prevent the lambda event body to
   contain an unexpected data format the header.content-type is
   removed.

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
            "marketplaceAccountId": "CustomerAWSAccountId",
            "customerIdentifier": "CustomerIdentifier",
            "productCode": "string",
            "entitlements": [
                {
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
