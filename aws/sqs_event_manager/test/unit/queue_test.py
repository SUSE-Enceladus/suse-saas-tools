from unittest.mock import MagicMock, patch

from sqs_event_manager.queue import get_queue_url, delete_message


def test_get_queue_url():
    arn = 'arn:aws:sqs:us-east-1:111122223333:my-queue'
    url = get_queue_url(arn)
    assert url == 'https://sqs.us-east-1.amazonaws.com/111122223333/my-queue'


@patch('boto3.client')
def test_delete_message(mock_boto_client):
    client = MagicMock()
    mock_boto_client.return_value = client
    delete_message('arn:aws:sqs:us-east-1:111122223333:my-queue', 'r123')
