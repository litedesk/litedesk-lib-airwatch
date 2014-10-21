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


from setuptools import setup


setup(name='cross7-lib-airwatch',
    version='0.0.1',
    description='Airwatch library for Cross7',
    author='Łukasz Biernot',
    author_email='lukasz.biernot@lgmail.com',
    url='http://laboratories.telekom.com',
    packages=[
        'cross7.lib.airwatch',
    ],
    package_dir={
        'cross7.lib.airwatch': 'src/cross7/lib/airwatch',
    },
    namespace_packages=['cross7', 'cross7.lib'],
    install_requires=['requests'],
    zip_safe=False,
    classifiers=[
        'Operating System :: Linux'
    ],
    keywords='cross7 airwatch',
)
