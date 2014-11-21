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


def check_response(exception_to_raise=None):
    def decorator(func):
        def proxy(self, *args, **kw):
            try:
                result = func(self, *args, **kw)
            except requests.HTTPError, http_error:
                error_message = http_error.response.json().get('Message')
                known_error_message = getattr(exception_to_raise, 'RESPONSE_MESSAGE')
                if known_error_message is not None and known_error_message == error_message:
                    raise exception_to_raise
                else:
                    raise http_error
            return result
        return proxy
    return decorator


class BaseObject(object):
    def __init__(self, client, *args, **kw):
        self._client = client
        for k, v in kw.items():
            setattr(self, k, v)
