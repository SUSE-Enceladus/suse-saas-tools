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
import json
from typing import Dict


class AWSSNSMessage:
    def __init__(self, message: Dict):
        self.message = message
        self.body = json.loads(self.__get('body'))

    def get_sns_content(self) -> Dict:
        message = self.body.get('Message') or {}
        if isinstance(message, dict):
            # message content is a dictionary already
            return message
        else:
            # message content is still a json string
            return json.loads(message.replace(' ', ''))

    @property
    def message_id(self) -> str:
        return self.__get('messageId')

    @property
    def category(self) -> str:
        return self.body.get('Type') or ''

    @property
    def customer_id(self) -> str:
        return self.get_sns_content().get('customer-identifier') or ''

    @property
    def product_code(self) -> str:
        return self.get_sns_content().get('product-code') or ''

    @property
    def action(self) -> str:
        return self.get_sns_content().get('action') or ''

    @property
    def offer_id(self) -> str:
        return self.get_sns_content().get('offer-identifier') or ''

    @property
    def free_trial_term_present(self) -> str:
        return self.get_sns_content().get('isFreeTrialTermPresent') or 'false'

    @property
    def event_source_arn(self) -> str:
        return self.__get('eventSourceARN')

    @property
    def receipt_handle(self) -> str:
        return self.__get('receiptHandle')

    def __get(self, key) -> str:
        return self.message[key] if self.message else ''
