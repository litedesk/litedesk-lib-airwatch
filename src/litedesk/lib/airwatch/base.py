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


import requests
from requests.auth import HTTPBasicAuth


class BaseObject(object):

    @classmethod
    def call_api(cls, endpoint, admin, password, token, data=None):
	headers = {'aw-tenant-code': token}
        response = requests.post(endpoint, data=data, auth=HTTPBasicAuth(admin, password), headers=headers)
        response.raise_for_status()
        return response
