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
from typing import Dict


def error_response(error: Dict, topic: str):
    return {
        'isBase64Encoded': False,
        'statusCode': error['ResponseMetadata']['HTTPStatusCode'],
        'body': {
            'errors': {
                topic: error['Error']['Message']
            }
        }
    }


def error_record(status_code: int, message: str) -> Dict:
    return {
        'ResponseMetadata': {
            'HTTPStatusCode': status_code
        },
        'Error': {
            'Message': message
        }
    }
