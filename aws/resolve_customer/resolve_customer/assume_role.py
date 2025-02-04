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


class AWSAssumeRole:
    """
    Get access tokens from the token service through the
    assumed role arn of the marketplace account
    """
    def __init__(self, role_arn, session_name):
        self.role_response = {}
        sts_client = boto3.client('sts')
        self.role_response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )

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
