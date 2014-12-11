# Copyright 2014, Deutsche Telekom AG - Laboratories (T-Labs)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from base import BaseObject


class App(BaseObject):
    @classmethod
    def search(cls, client, **kwargs):
        endpoint = 'mam/apps/search'
        response = client.call_api('GET', endpoint, params=kwargs)
        response.raise_for_status()
        return [
            cls(client, **attrs)
            for attrs in response.json().get('Application')
        ]

    def install(self, device):
        endpoint = 'mam/apps/public/{0}/install'.format(self.Id)
        response = self._client.call_api(
            'POST', endpoint,
            params={
                'DeviceId': device.Id,
                'MacAddress': device.MacAddress,
                'SerialNumber': device.SerialNumber,
                'Udid': device.Udid
            }
        )
        response.raise_for_status()

    def is_installed_on_device(self, device):
        return self.Id in (app.Id for app in device.installed_apps)


