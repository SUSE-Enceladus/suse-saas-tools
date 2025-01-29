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
import logging
from typing import Dict

logger = logging.getLogger()


def error_response(error: Dict, topic: str):
    return {
        'isBase64Encoded': False,
        'statusCode': error['ResponseMetadata']['HTTPStatusCode'],
        'body': {
            'errors': {
                topic: error['Error']['Message'],
                "Exception": error['Error']['Code']
            }
        }
    }


def error_record(status_code: int, message: str, kind: str = 'Unknown') -> Dict:
    return {
        'ResponseMetadata': {
            'HTTPStatusCode': status_code
        },
        'Error': {
            'Message': message,
            'Code': f'App.Error.{kind}'
        }
    }


def classify_error(
    error: Dict, aws_code: str, status_code: int, exception_name: str = ''
) -> Dict:
    error_code = error['Error']['Code']
    if error_code == aws_code:
        error['ResponseMetadata']['HTTPStatusCode'] = status_code
        if exception_name:
            error['Error']['Code'] = exception_name
    return error


def log_error(error: Dict) -> None:
    logger.error(error['Error']['Message'])
