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


from base import BaseObject, check_response


class UserAlreadyRegisteredError(Exception):
    pass


class UserAlreadyActivatedError(Exception):
    RESPONSE_MESSAGE = 'User is already active.'


class UserAlreadyEnrolledError(Exception):
    RESPONSE_MESSAGE = 'Enrollment User is already assigned to the User Group.'


class UserNotEnrolledError(Exception):
    RESPONSE_MESSAGE = 'Enrollment User is not assigned to the User Group.'


class UserNotActiveError(Exception):
    RESPONSE_MESSAGE = 'User is already inactive.'


class User(BaseObject):

    @classmethod
    def create(cls, client, username):
        if cls.get_remote(client, username) is not None:
            raise UserAlreadyRegisteredError

        endpoint = 'system/users/adduser'
        response = client.call_api('POST', endpoint, data={
            'username': username,
            'SecurityType': 'directory',
            })
        response.raise_for_status()
        return cls.get_remote(client, username)

    @classmethod
    def get_remote(cls, client, username):
        endpoint = 'system/users/search'
        response = client.call_api('GET', endpoint, params={'username': username})
        response.raise_for_status()
        if response.status_code == 204:
            return None
        try:
            users = [u for u in response.json().get('Users') if u.get('UserName') == username]
            return cls(client, **users.pop())
        except IndexError:
            return None

    def _get_id(self):
        if getattr(self, 'Id'): return self.Id.get('Value')
        return None

    def _set_id(self, value):
        self.Id = {'Value': value}

    @check_response(UserAlreadyActivatedError)
    def activate(self):
        endpoint = 'system/users/{0}/activate'.format(self.id)
        response = self._client.call_api('POST', endpoint)
        response.raise_for_status()

    @check_response(UserNotActiveError)
    def deactivate(self):
        endpoint = 'system/users/{0}/deactivate'.format(self.id)
        response = self._client.call_api('POST', endpoint)
        response.raise_for_status()

    @check_response(UserAlreadyEnrolledError)
    def add_to_group(self, group_id):
        endpoint = 'system/usergroups/{0}/user/{1}/addusertogroup'.format(group_id, self.id)
        response = self._client.call_api('POST', endpoint)
        response.raise_for_status()

    @check_response(UserNotEnrolledError)
    def remove_from_group(self, group_id):
        endpoint = 'system/usergroups/%s/user/%s/removeuserfromgroup' % (group_id, self.id)
        response = self._client.call_api('POST', endpoint)
        response.raise_for_status()

    def delete(self):
        endpoint = 'system/users/%s/delete' % (self.id, )
        response = self._client.call_api('DELETE', endpoint)
        response.raise_for_status()

    id = property(_get_id, _set_id)
