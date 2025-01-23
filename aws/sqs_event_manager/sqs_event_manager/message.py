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

logger = logging.getLogger('sqs_event_manager')
logger.setLevel('INFO')


class AWSSNSMessage:
    def __init__(self, message: dict):
        self.message = message

    def get_body(self) -> str:
        return self.__get('body')

    def get_sns_content(self) -> str:
        return self.get_body()['Message'] or {}

    @property
    def message_id(self) -> str:
        return self.__get('message_id')

    @property
    def customer_id(self) -> str:
        return self.get_sns_content()['customer-identifier']

    @property
    def product_code(self) -> str:
        return self.get_sns_content()['product-code']

    @property
    def action(self) -> str:
        return self.get_sns_content()['action']

    @property
    def event_source_arn(self) -> str:
        return self.__get('eventSourceARN')

    @property
    def receipt_handle(self) -> str:
        return self.__get('receipt_handle')

    def __get(self, key) -> str:
        return self.message[key] if self.message else ''
