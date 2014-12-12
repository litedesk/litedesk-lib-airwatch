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
from app import App


class Device(BaseObject):

    @classmethod
    def search(cls, client, **kwargs):
        endpoint = 'mdm/devices/search'
        response = client.call_api('GET', endpoint, params=kwargs)
        response.raise_for_status()
        try:
            return [
                cls(client, **attrs)
                for attrs in response.json().get('Devices')
            ]
        except:
            return []

    @property
    def installed_apps(self):
        endpoint = 'mdm/devices/udid/{0}/apps'.format(self.Udid)
        response = self._client.call_api('GET', endpoint)
        response.raise_for_status()
        return [
            App(self._client, **attrs)
            for attrs in response.json().get('DeviceApps')
        ]
