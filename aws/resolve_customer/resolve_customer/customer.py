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
import urllib.parse
from botocore.exceptions import ClientError
from resolve_customer.defaults import Defaults
from resolve_customer.assume_role import AWSAssumeRole
from resolve_customer.error import (
    error_record, log_error, classify_error
)
from typing import (
    Dict, List
)


class AWSCustomer:
    """
    Get AWS customer ID information from a marketplace token
    """
    def __init__(self, urlEncodedtoken: str):
        self.customer = {}
        self.error: Dict = {}
        self.error_list: List[Dict] = []
        config = Defaults.get_assume_role_config()
        role: Dict[str, Dict[str, str]] = config.get('role') or {}
        if urlEncodedtoken and role:
            token = urllib.parse.unquote(urlEncodedtoken)
            for region in sorted(role.keys()):
                try:
                    assume_role = AWSAssumeRole(
                        role[region]['arn'], role[region]['session']
                    )
                    marketplace = boto3.client(
                        'meteringmarketplace',
                        region_name=region,
                        aws_access_key_id=assume_role.get_access_key(),
                        aws_secret_access_key=assume_role.get_secret_access_key(),
                        aws_session_token=assume_role.get_session_token()
                    )
                    self.customer = marketplace.resolve_customer(
                        RegistrationToken=token
                    )
                    # success, clear all errors that happened so far
                    # and return from the constructor in this state
                    self.error = {}
                    self.error_list = []
                    return
                except ClientError as error:
                    self.error = error.response
                    # Classify group of errors into app exception and HTTP code
                    self.error = classify_error(
                        self.error, 'ExpiredTokenException',
                        400, 'App.Error.TokenException'
                    )
                    self.error = classify_error(
                        self.error, 'InvalidTokenException',
                        400, 'App.Error.TokenException'
                    )
                    self.error = classify_error(
                        self.error, 'ThrottlingException',
                        400, 'App.Error.TokenException'
                    )
                    self.error = classify_error(
                        self.error, 'DisabledApiException',
                        400, 'App.Error.TokenException'
                    )
                    self.error_list.append(self.error)

            # All attempts failed, log errors
            for issue in self.error_list:
                log_error(issue)
        else:
            if not urlEncodedtoken:
                self.error = error_record(
                    422, 'no marketplace token provided',
                    'MissingTokenException'
                )
            else:
                self.error = error_record(
                    500, 'no role provided',
                    'InternalServiceErrorException'
                )
            log_error(self.error)

    def get_id(self) -> str:
        return self.__get('CustomerIdentifier')

    def get_account_id(self) -> str:
        return self.__get('CustomerAWSAccountId')

    def get_product_code(self) -> str:
        return self.__get('ProductCode')

    def __get(self, key) -> str:
        return self.customer[key] if self.customer else ''
