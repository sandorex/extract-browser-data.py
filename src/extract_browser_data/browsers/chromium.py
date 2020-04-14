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

import json
import os
from typing import ClassVar, Dict, List, Type

from ..chromium import ChromiumProfile
from ..profile import Profile
from ..util import Platform
from .browser import Browser


class ChromiumBrowser(Browser):
   '''Browser class for Chromium-based browsers'''
   PROFILE_TYPE: ClassVar[Type[Profile]] = ChromiumProfile

   @classmethod
   def get_default_user_path(cls) -> Dict[Platform, str]:
      return {
          Platform.WIN32: '$LOCALAPPDATA/Chromium/User Data',
          Platform.LINUX: '$HOME/.config/chromium',
          Platform.MACOS: '$HOME/Library/Application Support/Chromium'
      }

   @classmethod
   def get_browser_name(cls) -> str:
      return 'Chromium'

   def get_profiles(self) -> List[Profile]:
      if not os.path.isdir(self.data_path):
         return []

      profiles = []
      for file in os.listdir(self.data_path):
         # skip system profile
         if file == 'System Profile':
            continue

         path = self.data_path.joinpath(file, 'Preferences')
         if path.is_file():
            with path.open() as f:
               preferences = json.load(f)

            # pylint: disable=not-callable
            profiles.append(
                self.PROFILE_TYPE(preferences['profile']['name'], path.parent))

      return profiles
