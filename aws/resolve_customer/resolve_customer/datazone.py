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
    error_record, log_error
)
from typing import (
    List, Dict
)


class AWSDataZone:
    """
    Get and manage subscriptions
    """
    def __init__(self, domain_id: str, subscription_id: str):
        self.subscription = {}
        self.error: Dict = {}
        self.error_list: List[Dict] = []
        config = Defaults.get_assume_role_config()
        role: Dict[str, Dict[str, str]] = config.get('role') or {}
        if domain_id and subscription_id and role:
            for region in sorted(role.keys()):
                try:
                    assume_role = AWSAssumeRole(
                        role[region]['arn'], role[region]['session']
                    )
                    datazone = boto3.client(
                        'datazone',
                        region_name=region,
                        aws_access_key_id=assume_role.get_access_key(),
                        aws_secret_access_key=assume_role.get_secret_access_key(),
                        aws_session_token=assume_role.get_session_token()
                    )
                    self.subscription = datazone.get_subscription(
                        domainIdentifier=domain_id,
                        identifier=subscription_id
                    )
                    # success, clear all errors that happened so far
                    # and return from the constructor in this state
                    self.error = {}
                    self.error_list = []
                    return
                except ClientError as error:
                    self.error = error.response
                    self.error_list.append(self.error)

            # All attempts failed, log errors
            for issue in self.error_list:
                log_error(issue)
        else:
            self.error = error_record(
                500, 'no domain_id/subscription_id and/or role provided',
                'InternalServiceErrorException'
            )
            log_error(self.error)

    def get_subscription(self) -> Dict:
        return self.subscription
