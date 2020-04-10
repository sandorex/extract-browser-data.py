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

import configparser
import os
from os.path import isfile as file_exists
from typing import Dict, List

from ..firefox import FirefoxProfile
from ..profile import Profile
from ..util import Platform, UnsupportedSchema
from .browser import Browser


class FirefoxBrowser(Browser):
   '''Browser class for Firefox-based browsers'''
   PROFILE_TYPE = FirefoxProfile

   @classmethod
   def get_default_user_path(cls) -> Dict[Platform, str]:
      return {
          Platform.WIN32: '$APPDATA/Mozilla/Firefox',
          Platform.LINUX: '$HOME/.mozilla/firefox',
          Platform.MACOS: '$HOME/Library/Application Support/Firefox'
      }

   @classmethod
   def get_browser_name(cls) -> str:
      return 'Firefox'

   def get_profiles(self) -> List[Profile]:
      FILE = self.data_path.joinpath('profiles.ini')
      parser = configparser.ConfigParser()

      if not file_exists(FILE):
         return []

      with open(FILE) as f:
         parser.read_file(f)

      # check schema version
      schema_version = parser.getint('General', 'Version')
      if schema_version != 2:
         raise UnsupportedSchema(FILE, schema_version)

      profiles = []
      for k in parser.keys():
         # skip non profile sections
         if k in ['DEFAULT', 'General']:
            continue

         # skip locked sections (i don't know what they are)
         if parser.getboolean(k, "Locked", fallback=False):
            continue

         name = parser.get(k, 'Name')
         path = parser.get(k, 'Path')
         default = parser.getboolean(k, 'Default', fallback=False)

         # create an absolute path if it's relative
         if parser.getboolean(k, 'IsRelative', fallback=False):
            path = self.data_path.joinpath(path)

         # normalize it just in case
         path = os.path.normpath(path)

         # pylint: disable=not-callable
         profiles.append(self.PROFILE_TYPE(name, path, default))

      return profiles
