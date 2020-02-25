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
import datetime
import configparser

from extract_browser_data.browser import Profile, Browser
from extract_browser_data.prelude import *


class FirefoxProfile(Profile):
   '''Profile class for Firefox browser'''
   def __init__(self, name, path, default=False):
      super().__init__(name, path)

      self.default = default

   def is_default_profile(self):
      """Checks if the profile is gonna run by default

      .. NOTICE::
         This function is Firefox only!
      """
      return self.default

   def is_profile_running(self):
      # firefox deletes 'sessionstore.jsonlz4' when it starts and it's created
      # again when it quits, so i am using it as a lockfile
      return not os.path.exists(os.path.join(self.path, 'sessionstore.jsonlz4'))

   def get_extension_list(self):
      FILE = os.path.join(self.path, 'extensions.json')

      with open(FILE, encoding='utf8') as f:
         data = json.load(f)

      # check schema version
      schema_version = data['schemaVersion']
      if schema_version != 31:
         raise util.UnsupportedSchema(FILE, schema_version)

      extensions = []
      for extension in data['addons']:
         # skip themes and such
         if extension["type"] != "extension":
            continue

         # skip builtin extensions
         if extension["location"] != "app-profile":
            continue

         # TODO add url or some id if possible
         extensions.append(extension["defaultLocale"]["name"].strip())

      return extensions

   def get_history(self, raw=False):
      # TODO raw later
      if raw:
         raise NotImplementedError()

      FILE = os.path.join(self.path, 'places.sqlite')

      # currently only getting url, title and time
      with util.connect_readonly(FILE) as conn:
         cursor = conn.cursor()
         cursor.execute(r'''SELECT url, title, last_visit_date
                            FROM moz_places ORDER BY last_visit_date DESC''')

         data = []
         for url, title, time_epoch in cursor.fetchall():

            if time_epoch is not None:
               # time is in microseconds since epoch so im dividing it
               time = datetime.datetime.utcfromtimestamp(
                   int(time_epoch / 1000000))
            else:
               time = None

            data.append((url, title, time))

      return data

   def get_bookmarks(self, raw=False):
      if not raw:
         raise NotImplementedError()

   def get_autofill(self, raw=False):
      if not raw:
         raise NotImplementedError()

   def get_cookies(self, raw=False):
      if not raw:
         raise NotImplementedError()


class FirefoxBrowser(Browser):
   '''Browser class for Firefox browser'''
   def is_browser_running(self):
      # firefox doesn't have a global lockfile so i am checking if any profile
      # is running
      return any([x.is_profile_running() for x in self.get_profiles()])

   def get_browser_name(self):
      return 'Firefox'

   def get_profiles(self):
      FILE = os.path.join(self.user_data_path, 'profiles.ini')
      parser = configparser.ConfigParser()

      with open(FILE) as f:
         parser.read_file(f)

      # check schema version
      schema_version = parser.getint('General', 'Version')
      if schema_version != 2:
         raise util.UnsupportedSchema(FILE, schema_version)

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
            path = os.path.join(self.user_data_path, path)

         # normalize it just in case
         path = os.path.normpath(path)

         profiles.append(FirefoxProfile(name, path, default=default))

      return profiles

   def find_profile(self, profile_name):
      for profile in self.get_profiles():
         if profile.get_profile_name() == profile_name:
            return profile

      return None

   def get_default_user_data_path(self):
      if WIN32:
         path = '$APPDATA/Mozilla/Firefox'
      elif LINUX:
         path = '$HOME/.mozilla/firefox'
      elif MACOS:  # TODO may be wrong
         path = '$HOME/Library/Application Support/Firefox'
      else:
         path = None

      return os.path.expandvars(os.path.normpath(path))
