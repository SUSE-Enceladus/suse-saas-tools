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
from botocore.exceptions import ClientError
from resolve_customer.error import log_error
from typing import Dict


class AWSAssumeRole:
    """
    Get access tokens from the token service through the
    assumed role arn of the marketplace account
    """
    def __init__(self, config: Dict[str, Dict[str, Dict[str, str]]]):
        self.role_response = {}
        self.error: Dict = {}
        self.error_count = 0
        self.region = ''
        role: Dict[str, Dict[str, str]] = config.get('role') or {}
        for region in role:
            try:
                sts_client = boto3.client('sts')
                self.role_response = sts_client.assume_role(
                    RoleArn=role[region]['arn'],
                    RoleSessionName=role[region]['session']
                )
                if self.get_access_key():
                    self.error = {}
                    self.region = region
                    break
                else:
                    self.error = {
                        'Error': {
                            'Message': 'assume_role has no data for {}'.format(
                                role[region]['arn']
                            )
                        }
                    }
                    self.error_count += 1
            except ClientError as error:
                self.error = error.response
                self.error_count += 1

        # log the last error as we expect the same reason
        # for all attempts
        if self.error:
            log_error(self.error)

    def get_region(self) -> str:
        return self.region

    def get_access_key(self) -> str:
        return self.__get('AccessKeyId')

    def get_secret_access_key(self) -> str:
        return self.__get('SecretAccessKey')

    def get_session_token(self) -> str:
        return self.__get('SessionToken')

    def get_expiration_date(self) -> str:
        return self.__get('Expiration')

    def __get(self, key) -> str:
        result = ''
        if self.role_response.get('Credentials'):
            result = self.role_response['Credentials'].get(key) or ''
        return result
