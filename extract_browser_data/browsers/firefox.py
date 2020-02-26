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
import configparser

from datetime import datetime
from extract_browser_data.browser import Profile, Browser
from extract_browser_data.prelude import *


def date_from_epoch(epoch):
   """Converts epoch to datetime

   Supports seconds, milliseconds, microseconds from epoch

   If `epoch` is `None` or too big for OS API to handle `epoch` will be returned
   """
   if epoch is None:
      return epoch

   if epoch > 99_999_999_999_999:  # >14 digits is in microseconds
      epoch /= 1_000_000
   elif epoch > 99_999_999_999:  # >11 digits is in milliseconds
      epoch /= 1_000

   # winapi cannot handle much bigger than this..
   if WIN32 and epoch > 32503680000:
      return epoch

   return datetime.utcfromtimestamp(epoch)


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

      # NOTE utf8 encoding here is required
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

         data = {}
         data['id'] = extension['id']
         data['version'] = extension['version']
         data['download-url'] = extension['sourceURI']

         # both installDate and updateDate are in milliseconds since epoch
         data['install-date'] = date_from_epoch(extension['installDate'])
         data['last-update'] = date_from_epoch(extension['updateDate'])

         # mozilla.org redirects to the page of the addon when id is supplied
         data[
             'url'] = 'https://addons.mozilla.org/en-US/firefox/addon/{}/'.format(
                 data['id'])

         # find english locale
         for locale in extension['locales']:
            if 'en' in locale['locales']:
               data['name'] = locale['name']
               data['description'] = locale['description']
               data['creator'] = locale['creator']

         # fallback
         if 'name' not in data:
            data['name'] = extension["defaultLocale"]['name']
            data['description'] = extension["defaultLocale"]['description']
            data['creator'] = extension["defaultLocale"]['creator']

         # some extensions have newlines at the end
         data['description'] = data['description'].strip()

         extensions.append(data)

      return extensions

   def get_history(self):
      with util.connect_readonly(os.path.join(self.path,
                                              'places.sqlite')) as conn:
         cursor = conn.cursor()
         cursor.execute(r'''SELECT url, title, last_visit_date
                            FROM moz_places ORDER BY last_visit_date DESC''')

         # time is in microseconds since epoch
         return [{
             'url': url,
             'title': title,
             'last_visit': date_from_epoch(last_visit)
         } for url, title, last_visit in cursor.fetchall()]

   def get_bookmarks(self):
      with util.connect_readonly(os.path.join(self.path,
                                              'places.sqlite')) as conn:
         cursor = conn.cursor()
         cursor.execute(r'''SELECT P.url, B.title, B.dateAdded, B.lastModified
                            FROM moz_bookmarks B
                            JOIN moz_places P
                            WHERE B.fk == P.id
                            ORDER BY B.lastModified DESC''')

         # TODO get the folder hiarcharchy

         # time is in microseconds since epoch
         return [{
             'url': url,
             'title': title,
             'date_added': date_from_epoch(date_added),
             'last_modified': date_from_epoch(last_modified)
         } for url, title, date_added, last_modified in cursor.fetchall()]

   def get_autofill(self):
      raise NotImplementedError()

   def get_cookies(self):
      with util.connect_readonly(os.path.join(self.path,
                                              'cookies.sqlite')) as conn:
         cursor = conn.cursor()
         cursor.execute(r'''SELECT
                            baseDomain,
                            name,
                            path,
                            value,
                            expiry,
                            creationTime,
                            lastAccessed
                            FROM moz_cookies
                            ORDER BY lastAccessed DESC''')

         # creationTime and lastAccessed is in microseconds since epoch
         # while expiry is in seconds since epoch
         return [{
             'base-domain': base_domain,
             'name': name,
             'path': path,
             'value': value,
             'expiry': date_from_epoch(expiry),
             'creation-time': date_from_epoch(creation_time),
             'last-accessed': date_from_epoch(last_accessed),
         } for base_domain, name, path, value, expiry, creation_time,
                 last_accessed in cursor.fetchall()]


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
