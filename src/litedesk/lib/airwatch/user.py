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


class User(BaseObject):

    @classmethod
    def create(cls, base_url, admin, password, token, username):
        endpoint = '{0}/API/v1/system/users/adduser'.format(base_url)
        content = '''
        <User xmlns="http://www.air-watch.com/servicemodel/resources">
        <UserName>{0}</UserName>
        <SecurityType>directory</SecurityType>
        </User>
        '''.format(username)
        return cls.call_api(endpoint, admin, password, token, content)

    @classmethod
    def activate(cls, base_url, admin, password, token, userid):
        endpoint = '{0}/API/v1/system/users/{1}/activate'.format(base_url, userid)
        return cls.call_api(endpoint, admin, password, token)

    @classmethod
    def deactivate(cls, base_url, admin, password, token, userid):
        endpoint = '{0}/API/v1/system/users/{1}/deactivate'.format(base_url, userid)
        return cls.call_api(endpoint, admin, password, token)

    @classmethod
    def assign_group(cls, base_url, admin, password, token, userid, groupid):
        endpoint = '{0}/API/v1/system/usergroups/{1}/user/{2}/addusertogroup'.format(base_url, userid, groupid)
        return cls.call_api(endpoint, admin, password, token)

    @classmethod
    def unassign_group(cls, base_url, admin, password, token, userid, groupid):
        endpoint = '{0}/API/v1/system/usergroups/{1}/user/{2}/removeuserfromgroup'.format(base_url, userid, groupid)
        return cls.call_api(endpoint, admin, password, token)
