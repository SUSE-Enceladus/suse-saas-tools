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
from typing import List

logger = logging.getLogger()


class AWSCustomerEntitlement:
    """
    Get AWS customer entitlements for given customer ID and product code
    """
    def __init__(self, customer_id: str, product_code: str):
        self.entitlements = {}
        self.error = ''
        if customer_id and product_code:
            try:
                marketplace = boto3.client('marketplace-entitlement')
                self.entitlements = marketplace.get_entitlements(
                    {
                        'ProductCode': product_code,
                        'Filter': {'CUSTOMER_IDENTIFIER': [customer_id]}
                    }
                )
            except Exception as error:
                self.error = f'marketplace-entitlement client failed with: {error}'
                logger.error(self.error)
        else:
            self.error = 'no customer_id and/or product_code provided'
            logger.error(self.error)

    def get_entitlements(self) -> List[dict]:
        return self.entitlements.get('Entitlements') or []
