AWS SQS interface

React on SQS events connected as lambdas. 

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

* 500: Internal Server Error
* 503: Service unavailable, any non AWS ClientException
* HTTP_STATUS_CODE: HTTP status code as it was provided by the client call
