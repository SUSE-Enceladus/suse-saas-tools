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
from resolve_customer.defaults import Defaults
from resolve_customer.assume_role import AWSAssumeRole
from resolve_customer.error import (
    error_record, log_error, classify_error
)
from typing import List


class AWSCustomerEntitlement:
    """
    Get AWS customer entitlements for given customer ID and product code
    """
    def __init__(self, customer_id: str, product_code: str):
        self.entitlements = {}
        self.error = {}
        if customer_id and product_code:
            try:
                assume_role_config = Defaults.get_assume_role_config()
                assume_role = AWSAssumeRole(
                    assume_role_config['role']['arn'],
                    assume_role_config['role']['session']
                )
                marketplace = boto3.client(
                    'marketplace-entitlement',
                    region_name=assume_role_config['role']['region'],
                    aws_access_key_id=assume_role.get_access_key(),
                    aws_secret_access_key=assume_role.get_secret_access_key(),
                    aws_session_token=assume_role.get_session_token()
                )
                self.entitlements = marketplace.get_entitlements(
                    ProductCode=product_code,
                    Filter={'CUSTOMER_IDENTIFIER': [customer_id]}
                )
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
                log_error(self.error)
        else:
            self.error = error_record(
                500, 'no customer_id and/or product_code provided',
                'InternalServiceErrorException'
            )
            log_error(self.error)

    def get_entitlements(self) -> List[dict]:
        entitlements = []
        if self.entitlements:
            for entitelement in self.entitlements['Entitlements']:
                entitlements.append(
                    {
                        'customerIdentifier': entitelement.get(
                            'CustomerIdentifier'
                        ),
                        'productCode': entitelement.get(
                            'ProductCode'
                        ),
                        'expirationDate': format(
                            entitelement.get('ExpirationDate')
                        ),
                        'dimension': entitelement.get(
                            'Dimension'
                        ),
                        'value': {
                            'booleanValue': entitelement['Value'].get(
                                'BooleanValue'
                            ),
                            'doubleValue': entitelement['Value'].get(
                                'DoubleValue'
                            ),
                            'integerValue': entitelement['Value'].get(
                                'IntegerValue'
                            ),
                            'stringValue': entitelement['Value'].get(
                                'StringValue'
                            )
                        }
                    }
                )
        return entitlements
