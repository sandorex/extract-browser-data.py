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

import os
import json

from ...chromium import ChromiumProfile
from .browser import Browser
from .prelude import *


class ChromiumBrowser(Browser):
   '''Browser class for Chromium-based browsers'''
   PROFILE_TYPE = ChromiumProfile

   @classmethod
   def get_default_user_path(cls):
      if WIN32:
         return '$LOCALAPPDATA/Chromium/User Data'

      if LINUX:
         return '$HOME/.config/chromium'

      if MACOS:
         return '$HOME/Library/Application Support/Chromium'

      return None

   @classmethod
   def get_browser_name(cls):
      return 'Chromium'

   def get_profiles(self):
      if not os.path.exists(self.data_path):
         return []

      profiles = []
      for file in os.listdir(self.data_path):
         # skip system profile
         if file == 'System Profile':
            continue

         path = self.data_path.joinpath(file, 'Preferences')
         if path.exists() and path.is_file():
            with path.open() as f:
               preferences = json.load(f)

            # pylint: disable=not-callable
            profiles.append(
                self.PROFILE_TYPE(preferences['profile']['name'], path.parent))

      return profiles
