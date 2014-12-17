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

from requests.exceptions import HTTPError

from base import BaseObject
from user import User
from app import App


class UserGroup(BaseObject):

    @staticmethod
    def usernames_by_group_id(client, group_id):
        endpoint = 'system/usergroups/{0}/users'.format(group_id)
        response = client.call_api('GET', endpoint)
        response.raise_for_status()
        return [
            u.get('UserName') for u in response.json().get('EnrollmentUser')
        ]

    @classmethod
    def get_remote(cls, client, group_name):
        endpoint = 'system/usergroups/custom/search'
        params = {'groupname': group_name}
        response = client.call_api('GET', endpoint, params=params)
        response.raise_for_status()
        return cls(client, **response.json().get('UserGroup')[0])

    def _membership_change_common(self, user, endpoint_suffix, if_exists):
        # if_exists says if operation is valid when user is already a member
        # checking for identity cause True and False are singletons
        if if_exists is not (user.UserName in self.usernames_by_group_id(
            self._client, self.UserGroupId
        )):
            return
        endpoint = 'system/usergroups/{0}/user/{1}/{2}'.format(
            self.UserGroupId, user.id, endpoint_suffix
        )
        response = self._client.call_api('POST', endpoint)
        response.raise_for_status()

    def add_member(self, user):
        self._membership_change_common(user, 'addusertogroup', False)

    def remove_member(self, user):
        self._membership_change_common(user, 'removeuserfromgroup', True)


class SmartGroup(BaseObject):

    @classmethod
    def create(cls, client, **kwargs):
        endpoint = 'mdm/smartgroups/create'
        response = client.call_api('POST', endpoint, data=kwargs)
        response.raise_for_status()
        return cls.get_remote(client, response.text)

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
    def get_remote(cls, client, smart_group_id):
        endpoint = 'mdm/smartgroups/{0}'.format(smart_group_id)
        response = client.call_api('GET', endpoint)
        response.raise_for_status()
        return cls(client, **response.json())

    def delete(self):
        endpoint = 'mdm/smartgroups/{0}/delete'.format(self.SmartGroupID)
        response = self._client.call_api('DELETE', endpoint)
        response.raise_for_status()

    def _update(self, **kwargs):
        endpoint = 'mdm/smartgroups/{0}/update'.format(self.SmartGroupID)
        response = self._client.call_api('POST', endpoint, data=kwargs)
        response.raise_for_status()

    @property
    def members(self):
        return [
            User.get_remote(self._client, user['Name'])
            for user in self.UserAdditions
        ]

    @property
    def apps(self):
        return [
            app for app in App.search(self._client, pagesize=5000)
            if self.SmartGroupID in (
                smart_group['Id'] for smart_group in app.SmartGroups
            )
        ]

    @staticmethod
    def __user_additions_to_set(user_additions):
        return {(user['Id'], user['Name']) for user in user_additions}

    @staticmethod
    def __user_additons_from_set(user_additions_set):
        return [{'Id': user[0], 'Name': user[1]} for user in user_additions_set]

    def __membership_change_common(self):
        user_additions_set = self.__user_additions_to_set(self.UserAdditions)
        count = len(user_additions_set)
        yield user_additions_set
        if count != len(user_additions_set):
            user_additions = self.__user_additons_from_set(user_additions_set)
            self._update(UserAdditions=user_additions)
            self.UserAdditions = user_additions

    def add_member(self, user):
        for user_additions_set in self.__membership_change_common():
            user_additions_set.add((str(user.id), user.UserName))

    def remove_member(self, user):
        for user_additions_set in self.__membership_change_common():
            user_additions_set.discard((str(user.id), user.UserName))


class UserGroupHacked(UserGroup):
    """
    This class exists because of AirWatch backend bug in SmartGroups.
    Currently adding/removing member of UserGroup is not guaranteed
    to be reflected in SmartGroup, resulting in unreliable app install/uninstall
    on user device. Once AirWatch bug is fixed, normal UserGroup should be used
    instead of this class.
    """

    SMART_GROUP_PREFIX = 'Hacked'

    def _membership_change_common(self, *args, **kw):
        super(UserGroupHacked, self)._membership_change_common(*args, **kw)
        smart_groups = self._smart_groups
        for smart_group in smart_groups:
            if (
                smart_group.Name.startswith(self.SMART_GROUP_PREFIX)
                or '{0} {1}'.format(self.SMART_GROUP_PREFIX, smart_group.Name) in (
                    sg.Name for sg in smart_groups
                )
            ):
                print 'Skipping Smart Group {0}'.format(smart_group.Name)
                continue
            self._replace_smart_group(smart_group)

    @property
    def _smart_groups(self):
        return [
            smart_group for smart_group in SmartGroup.search(self._client)
            if self.UserGroupName in (
                user_group['Name'] for user_group in smart_group.UserGroups
            )
        ]

    def _replace_smart_group(self, smart_group):
        name = smart_group.Name
        temp_name = 'Hacked {0}'.format(name)
        print 'Creating Smart Group {0}'.format(temp_name)
        try:
            new_smart_group = SmartGroup.create(
                self._client,
                DeviceAdditions=smart_group.DeviceAdditions,
                DeviceExclusions=smart_group.DeviceExclusions,
                ManagedByOrganizationGroupId=smart_group.ManagedByOrganizationGroupId,
                Models=smart_group.Models,
                Name=temp_name,
                OperatingSystems=smart_group.OperatingSystems,
                OrganizationGroups=smart_group.OrganizationGroups,
                Ownerships=smart_group.Ownerships,
                Platforms=smart_group.Platforms,
                UserAdditions=smart_group.UserAdditions,
                UserExclusions=smart_group.UserExclusions,
                UserGroups=smart_group.UserGroups
            )
        except HTTPError, e:
            # Amazing, AirWatch throws 400 but Smart Group is created :)
            if e.response.status_code != 400:
                raise
            else:
                new_smart_group = [
                    sg for sg in SmartGroup.search(self._client)
                    if sg.Name == temp_name
                ][0]
        print 'Moving apps from {0} to {1}'.format(name, temp_name)
        self._move_apps(smart_group, new_smart_group)
        print 'Deleting Smart Group {0}'.format(name)
        smart_group.delete()
        print 'Renaming Smart Group {0} to {1}'.format(temp_name, name)
        new_smart_group._update(Name=name)
        print 'Smart Group {0} replaced'.format(name)

    def _move_apps(self, smart_group, new_smart_group):
        for app in smart_group.apps:
            print 'Adding app {0} to Smart Group {1}'.format(app.ApplicationName, new_smart_group.Name)
            app.add_smart_group(new_smart_group)
            print 'Removing app {0} from Smart Group {1}'.format(app.ApplicationName, smart_group.Name)
            app.delete_smart_group(smart_group)
