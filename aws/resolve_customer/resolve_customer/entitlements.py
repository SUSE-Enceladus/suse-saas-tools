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
from resolve_customer.defaults import Defaults
from resolve_customer.assume_role import AWSAssumeRole
from resolve_customer.error import (
    error_record, log_error, classify_error
)
from typing import (
    List, Dict
)

logger = logging.getLogger('marketplace_entitlement')
logger.setLevel('INFO')


class AWSCustomerEntitlement:
    """
    Get AWS customer entitlements for given customer ID and product code
    """
    def __init__(self, customer_id: str, product_code: str):
        self.entitlements = {}
        self.error: Dict = {}
        self.error_list: List[Dict] = []
        config = Defaults.get_assume_role_config()
        role: Dict[str, Dict[str, str]] = config.get('role') or {}
        if customer_id and product_code and role:
            logger.info(
                'requesting entitlements for customer {} and product {}'.format(
                    customer_id, product_code
                )
            )
            for region in sorted(role.keys()):
                try:
                    assume_role = AWSAssumeRole(
                        role[region]['arn'], role[region]['session']
                    )
                    marketplace = boto3.client(
                        'marketplace-entitlement',
                        region_name='us-east-1',
                        aws_access_key_id=assume_role.get_access_key(),
                        aws_secret_access_key=assume_role.get_secret_access_key(),
                        aws_session_token=assume_role.get_session_token()
                    )
                    self.entitlements = marketplace.get_entitlements(
                        ProductCode=product_code,
                        Filter={'CUSTOMER_IDENTIFIER': [customer_id]}
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
                        self.error, 'InvalidParameterException',
                        400, 'App.Error.EntitlementException'
                    )
                    self.error = classify_error(
                        self.error, 'ThrottlingException',
                        400, 'App.Error.EntitlementException'
                    )
                    self.error_list.append(self.error)

            # All attempts failed, log errors
            for issue in self.error_list:
                log_error(issue)
        else:
            self.error = error_record(
                500, 'no customer_id/product_code and/or role provided',
                'InternalServiceErrorException'
            )
            log_error(self.error)

    def get_entitlements(self) -> List[dict]:
        result_entitlements: List = []
        if self.entitlements:
            entitlements = self.entitlements.get('Entitlements') or []
            for entitlement in entitlements:
                result_entitlements.append(
                    {
                        'expirationDate': format(
                            entitlement.get('ExpirationDate')
                        ),
                        'dimension': entitlement.get(
                            'Dimension'
                        ),
                        'value': {
                            'booleanValue': bool(
                                entitlement['Value'].get('BooleanValue')
                            ),
                            'doubleValue': float(
                                entitlement['Value'].get('DoubleValue') or 0
                            ),
                            'integerValue': int(
                                entitlement['Value'].get('IntegerValue') or 0
                            ),
                            'stringValue': format(
                                entitlement['Value'].get('StringValue') or ''
                            )
                        }
                    }
                )
        return result_entitlements
