#!/usr/bin/python3.11
import typer
import logging
import boto3
import json
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def publish_message(topic, message, attributes={}, fifo=True):
    """
    Publishes a message, with attributes, to a topic.
    Subscriptions can be filtered based on message attributes
    so that a subscription receives messages only
    when specified attributes are present.

    :param topic: The topic to publish to.
    :param message: The message to publish.
    :param attributes:
        The key-value attributes to attach to the message. Values
        must be either `str` or `bytes`.
    :return: The ID of the message.
    """
    try:
        att_dict = {}
        for key, value in attributes.items():
            if isinstance(value, str):
                att_dict[key] = {"DataType": "String", "StringValue": value}
            elif isinstance(value, bytes):
                att_dict[key] = {"DataType": "Binary", "BinaryValue": value}
        if fifo:
            response = topic.publish(
                Message=message,
                MessageAttributes=att_dict,
                MessageGroupId='SaaS_Dev'
            )
        else:
            response = topic.publish(
                Message=message,
                MessageAttributes=att_dict
            )
        message_id = response["MessageId"]
        logger.info(
            "Published message with attributes %s to topic %s.",
            attributes,
            topic.arn,
        )
    except ClientError:
        logger.exception("Couldn't publish message to topic %s.", topic.arn)
        raise
    else:
        return message_id


def main(messagefile: str, profile: str = 'suse-pct-prod'):
    try:
        with open(messagefile) as json_message_file:
            message = json.load(json_message_file)

        session = boto3.Session(profile_name=profile)
        sns = session.resource('sns')
        topic = sns.create_topic(
            Name='test-sns-topic-saas', Attributes={'FifoTopic': 'false'}
        )
        publish_message(
            topic, json.dumps(message), {}, False
        )
    except Exception as issue:
        logger.error(f'Failed to publish message: {issue}')


if __name__ == "__main__":
    typer.run(main)
