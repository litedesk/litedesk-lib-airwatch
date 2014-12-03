#!/usr/bin/env python

# Copyright 2014, Deutsche Telekom AG - Laboratories (T-Labs)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from base import BaseObject


class UserGroup(BaseObject):

    @staticmethod
    def usernames_by_group_id(client, group_id):
        endpoint = 'system/usergroups/{0}/users'.format(group_id)
        response = client.call_api('GET', endpoint)
        response.raise_for_status()
        return [user.get('UserName') for user in response.json().get('EnrollmentUser')]


class SmartGroup(BaseObject):

    @classmethod
    def search(cls, client, **kwargs):
        endpoint = '/mdm/smartgroups/search'
        response = client.call_api('GET', endpoint, params=kwargs)
        response.raise_for_status()
        return [
            self.__class__(client, **attrs)
            for attrs in response.json()
        ]

    def update(self, **kwargs):
        endpoint = 'mdm/smartgroups/{0}/update'.format(self.id)
        response = client.call_api('POST', endpoint, data=kwargs)
        response.raise_for_status()

