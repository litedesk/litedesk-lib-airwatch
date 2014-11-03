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

import json

import requests


class Client(object):
    def __init__(self, server_url, username, password, api_token):
        self.server_url = server_url
        self.token = api_token
        self._session = requests.Session()
        self._session.auth = (username, password)
        self._session.headers.update({
            'aw-tenant-code': self.token,
            'Accept': 'application/json'
            })

    def call_api(self, method, endpoint, data=None, **kw):
        if data is not None:
            kw['data'] = json.dumps(data)

        full_url = '%s/API/v1/%s' % (self.server_url, endpoint)

        return {
            'GET': self._session.get,
            'PUT': self._session.put,
            'POST': self._session.post,
            'DELETE': self._session.delete
            }.get(method, self._session.get)(full_url, **kw)
