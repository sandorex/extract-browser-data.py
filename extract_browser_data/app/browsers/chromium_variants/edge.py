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

from ..chromium import ChromiumBrowser
from ..prelude import *


class EdgeBrowser(ChromiumBrowser):
   '''Browser class for Edge browser that is based on Chromium'''
   @classmethod
   def get_browser_name(self):
      return 'Edge'

   @classmethod
   def get_default_user_path(self):
      # TODO i couldn't find the path for other operating systems
      return '$LOCALAPPDATA/Microsoft/Edge/User Data'
