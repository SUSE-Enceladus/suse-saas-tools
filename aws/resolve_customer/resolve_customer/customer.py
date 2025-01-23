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
import boto3
from botocore.exceptions import ClientError
from resolve_customer.error import error_record

logger = logging.getLogger()


class AWSCustomer:
    """
    Get AWS customer ID information from a marketplace token
    """
    def __init__(self, token: str):
        self.customer = {}
        self.error = {}
        if token:
            try:
                marketplace = boto3.client('meteringmarketplace')
                self.customer = marketplace.resolve_customer(
                    RegistrationToken=token
                )
            except ClientError as error:
                self.error = error.response
                logger.error(self.error['Error']['Message'])
        else:
            self.error = error_record(422, 'no marketplace token provided')
            logger.error(self.error['Error']['Message'])

    def get_id(self) -> str:
        return self.__get('CustomerIdentifier')

    def get_account_id(self) -> str:
        return self.__get('CustomerAWSAccountId')

    def get_product_code(self) -> str:
        return self.__get('ProductCode')

    def __get(self, key) -> str:
        return self.customer[key] if self.customer else ''
