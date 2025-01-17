# Copyright (c) 2025 SUSE LLC.  All rights reserved.
#
# This file is part of suse-saas-tools
#
# suse-saas-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mash is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mash.  If not, see <http://www.gnu.org/licenses/>
#

import boto3


def get_queue_url(arn: str) -> str:
    """Return queue url based on arn"""
    prefix, region, account, queue = arn.rsplit(':', maxsplit=3)
    return f'https://sqs.{region}.amazonaws.com/{account}/{queue}'


def delete_message(queue_arn: str, receipt_handle: str):
    """Delete the message from the queue"""
    queue_url = get_queue_url(queue_arn)
    client = boto3.client('sqs')

    client.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
