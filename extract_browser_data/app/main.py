# (https://github.com/sandorex/extract-browser-data.py)
# extract-browser-data
#
# Copyright 2020 Aleksandar Radivojevic
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

from .browsers import get_browsers


def main(args=sys.argv):
   print('profiles found:')
   for browser in get_browsers():
      b = browser()
      print(' ' * 2, b.get_browser_name())
      for profile in b.get_profiles():
         print(' ' * 4, "'{}' at '{}'".format(profile.name, profile.path))


def main_chromium(args=sys.argv):
   print('main chromium')


def main_firefox(args=sys.argv):
   print('main firefox')
