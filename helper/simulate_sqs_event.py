#!/usr/bin/python3.11
import typer
import logging
import boto3
import json

logger = logging.getLogger(__name__)


def main(
    messagefile: str,
    profile: str = 'suse-pct-prod',
    queue: str = 'test-event-queue-saas'
):
    try:
        with open(messagefile) as json_message_file:
            message = json.load(json_message_file)

        message_dump = json.dumps(message)
        data = {
            'Type': 'Notification',
            'MessageId': 'uuid',
            'TopicArn': 'arn:aws:sns:us-east-1:XXX:aws-mp-entitlement-notification-XX',
            'Message': message_dump,
            'Timestamp': '2025-01-15 16:31:50',
            'SignatureVersion': '1',
            'Signature': 'abc123',
            'SigningCertURL': 'string',
            'UnsubscribeURL': 'string'
        }
        json_data = json.dumps(data)

        session = boto3.Session(profile_name=profile)
        sqs = session.resource('sqs')

        alias_queue = sqs.get_queue_by_name(QueueName=queue)
        logger.info('Got queue {} with URL {}'.format(queue, alias_queue.url))

        # send to standard queues. For fifo queues use this:
        # alias_queue.send_message(
        #     MessageBody=json_data, MessageGroupId='586474de88e11'
        # )
        alias_queue.send_message(
            MessageBody=json_data, MessageAttributes={}
        )
    except Exception as issue:
        logger.error(f'Failed to send message: {issue}')


if __name__ == "__main__":
    typer.run(main)
