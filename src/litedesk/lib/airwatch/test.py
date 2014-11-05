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


import os
import unittest

from client import Client
from user import User

try:
    from litedesk.lib.active_directory.session import Session
    from litedesk.lib.active_directory.classes.base import Company as ADCompany, User as ADUser
except ImportError:
    raise Exception(
        'These tests depend on missing libraries. To install them invoke `pip install -r test_requirements.txt`.'
    )


class UserTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.url = os.environ['LITEDESK_LIB_AIRWATCH_URL']
            cls.admin = os.environ['LITEDESK_LIB_AIRWATCH_ADMIN']
            cls.password = os.environ['LITEDESK_LIB_AIRWATCH_PASSWORD']
            cls.token = os.environ['LITEDESK_LIB_AIRWATCH_TOKEN']
            cls.ad_url = os.environ['LITEDESK_LIB_ACTIVE_DIRECTORY_URL']
            cls.ad_dn = os.environ['LITEDESK_LIB_ACTIVE_DIRECTORY_DN']
            cls.ad_password = os.environ['LITEDESK_LIB_ACTIVE_DIRECTORY_PASSWORD']
        except KeyError:
            raise Exception(
                'This tests require environment variables (LITEDESK_LIB_AIRWATCH_URL, LITEDESK_LIB_AIRWATCH_ADMIN, '
                'LITEDESK_LIB_AIRWATCH_PASSWORD, LITEDESK_LIB_AIRWATCH_TOKEN, LITEDESK_LIB_ACTIVE_DIRECTORY_URL, '
                'LITEDESK_LIB_ACTIVE_DIRECTORY_DN, LITEDESK_LIB_ACTIVE_DIRECTORY_PASSWORD) to be set.'
            )

    def setUp(self):
        self.session = Session(self.ad_url, self.ad_dn, self.ad_password)
        self.ad_company = ADCompany(self.session, ou='test_company')
        self.ad_company.save()
        self.ad_user = ADUser(
            self.session,
            parent=self.ad_company,
            s_am_account_name='test.user',
            given_name='Test',
            sn='User',
            mail='test.user@example.com',
            display_name='Test User'
        )
        self.ad_user.save()
        self.client = Client(
            self.url,
            self.admin,
            self.password,
            self.token
        )

    def test_create_user(self):
        user = User.create(self.client, self.ad_user.s_am_account_name)
        self.assertIsNotNone(user.id)
        user.delete()

    def test_delete_user(self):
        user = User.create(self.client, self.ad_user.s_am_account_name)
        user.delete()
        self.assertIsNone(User.get_remote(self.client, self.ad_user.s_am_account_name))

    def test_activate_user(self):
        user = User.create(self.client, self.ad_user.s_am_account_name)
        user.activate()
        self.assertEqual(User.get_remote(self.client, self.ad_user.s_am_account_name).Status, True)
        user.delete()

    def test_deactivate_user(self):
        user = User.create(self.client, self.ad_user.s_am_account_name)
        user.activate()
        user.deactivate()
        self.assertEqual(User.get_remote(self.client, self.ad_user.s_am_account_name).Status, False)
        user.delete()

    def test_add_user_to_group(self):
        user = User.create(self.client, self.ad_user.s_am_account_name)
        user.activate()
        user.add_to_group(2819)
        """TODO: Assert user in group"""
        user.delete()

    def test_remove_user_from_group(self):
        user = User.create(self.client, self.ad_user.s_am_account_name)
        user.activate()
        user.add_to_group(2819)
        user.remove_from_group(2819)
        """TODO: Assert user NOT in group"""
        user.delete()

    def tearDown(self):
        self.ad_user.delete()
        self.ad_company.delete()


if __name__ == '__main__':
    unittest.main()