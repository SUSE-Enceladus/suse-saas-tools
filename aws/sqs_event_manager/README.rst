AWS SQS Event Manager
---------------------

The SQS Event Manager reacts on SQS events from a given sns topic.
The topic of the messages are marketplace entitlement change notifications.
The manager runs as a Lambda function and handles the events when the come
in. The cusomer entitlement data is collected and passed on to the
API setup in the coniguration file.

Higlevel Deployment Plan
------------------------

To deploy the sqs_event_manager code in the AWS cloud the
following services must be used:

* AWS Elastic Container Registry
* AWS Lambda

For the deployment the following steps are needed:

1. Push the SUSE SaaS tool chain container to an AWS
   Elastic Container Registry

2. Create an AWS Lambda function from the container URL
   created in 1. The Lambda has to provide the following
   configuration settings:

   * Image -> CMD override -> sqs_event_handler.lambda_handler
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

   Additionally a statement for SQS execution:

   .. code::

       {
            "Effect": "Allow",
            "Action": [
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            "Resource": "arn:aws:sqs:us-east-1:123:my-queue"
        }

  This allows the Lambda function to receive and delete messages from
  the event queue.

4. Setup event source mapping from the queue to the Lambda function:

  Run the following command using AWS CLI:

  .. code::

      aws lambda create-event-source-mapping \
        --function-name {name of Lambda function} \
        --batch-size 10 \
        --event-source-arn arn:aws:sqs:us-east-1:123:my-queue

EVENTS
------

The SNS Topics have the following event format:

.. code::

   {
      "Records": [
          {
              "messageId": "uuid",
              "receiptHandle": "string",
              "body": {
                  "Type" : "Notification",
                  "MessageId" : "uuid",
                  "TopicArn" : "arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XXX",
                  "Message" : {
                      "action": "entitlement-updated",
                      "customer-identifier": "string",
                      "product-code": "string"
                  },
                  "Timestamp" : "2025-01-15 16:31:50",
                  "SignatureVersion" : "1",
                  "Signature" : "abc123",
                  "SigningCertURL" : "string",
                  "UnsubscribeURL" : "string"
              },
              "attributes": {
                  "ApproximateReceiveCount": "1",
                  "SentTimestamp": "1545082649183",
                  "SenderId": "string",
                  "ApproximateFirstReceiveTimestamp": "1545082649185"
              },
              "messageAttributes": {},
              "md5OfBody": "string",
              "eventSource": "aws:sqs",
              "eventSourceARN": "arn:aws:sqs:us-east-1:111122223333:my-queue",
              "awsRegion": "us-east-1"
          }
      ]
  }

REQUEST
--------

.. code::

      {
          "marketplaceIdentifier": "AWS",
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
-------------------------------

* 500: App.Error.InternalServiceErrorException

Pass through exceptions:
------------------------

* HTTP_STATUS_CODE: HTTP status code as it was provided by the client call
