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

from extract_browser_data.browsers import register_browser
from extract_browser_data.browser import Profile, Browser
from extract_browser_data.prelude import *


class ChromiumProfile(Profile):
   '''Profile class for Chromium-based browsers'''
   def is_profile_running(self):
      '''Checks if a browser instance is running while using this profile'''
      raise NotImplementedError()

   def get_extension_list(self):
      '''Returns list of extensions installed by user'''
      raise NotImplementedError()

   def get_history(self):
      '''Returns browsing history'''
      raise NotImplementedError()

   def get_bookmarks(self):
      '''Returns bookmarks'''
      raise NotImplementedError()

   def get_cookies(self):
      '''Returns autofill data'''
      raise NotImplementedError()


class ChromiumBrowser(Browser):
   '''Browser class for Chromium-based browsers'''
   def is_browser_running(self):
      # lockfile exists if any profile is running
      return self.user_data_path.joinpath('lockfile').exists()

   def get_browser_name(self):
      return 'Chromium'

   def get_profiles(self):
      profiles = []
      for file in os.listdir(self.user_data_path):
         # skip system profile
         if file == 'System Profile':
            continue

         path = self.user_data_path.joinpath(file, 'Preferences')
         if path.exists() and path.is_file():
            with path.open() as f:
               preferences = json.load(f)

            # nothing important other than the name is contained in the file
            profiles.append(
                ChromiumProfile(preferences['profile']['name'], path.parent,
                                self.get_browser_name()))

      return profiles

   def get_default_user_data_path(self):
      if WIN32:
         path = '$LOCALAPPDATA/Google/Chrome/User Data'
         # path = '$LOCALAPPDATA/BraveSoftware/Brave-Browser/User Data/'
      elif LINUX:
         path = '~/.config/google-chrome'
      elif MACOS:
         path = '$HOME/Library/Application Support/Google/Chrome'

      return os.path.expandvars(os.path.normpath(path))


register_browser(ChromiumBrowser())
