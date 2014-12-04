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

import copy

from base import BaseObject
from user import User


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
            cls.get_remote(client, attrs['SmartGroupID'])
            for attrs in response.json().get('SmartGroups')
        ]

    @classmethod
    def get_remote(cls, client, id):
        endpoint = 'mdm/smartgroups/{0}'.format(id)
        response = client.call_api('GET', endpoint)
        response.raise_for_status()
        return cls(client, **response.json())

    def __update(self, **kwargs):
        endpoint = 'mdm/smartgroups/{0}/update'.format(self.SmartGroupID)
        response = self._client.call_api('POST', endpoint, data=kwargs)
        response.raise_for_status()

    @property
    def members(self):
        return [
            User.get_remote(self._client, user['Name'])
            for user in self.UserAdditions
        ]

    @staticmethod
    def __user_additions_to_set(user_additions):
        return {(user['Id'], user['Name']) for user in user_additions}

    @staticmethod
    def __user_additons_from_set(user_additions_set):
        return [{'Id': user[0], 'Name': user[1]} for user in user_additions_set]

    def __membership_manipulation_common(self):
        user_additions_set = self.__user_additions_to_set(self.UserAdditions)
        count = len(user_additions_set)
        yield user_additions_set
        if count != len(user_additions_set):
            user_additions = self.__user_additons_from_set(user_additions_set)
            self.__update(UserAdditions=user_additions)
            self.UserAdditions = user_additions

    def add_member(self, user):
        for user_additions_set in self.__membership_manipulation_common():
            user_additions_set.add((str(user.id), user.UserName))

    def remove_member(self, user):
        for user_additions_set in self.__membership_manipulation_common():
            user_additions_set.discard((str(user.id), user.UserName))
