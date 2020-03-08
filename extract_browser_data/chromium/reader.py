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

from ..reader import Reader
from .. import util
from .files import (PREFERENCES, HISTORY, LOGIN_DATA, WEB_DATA, COOKIES,
                    SECURE_PREFERENCES, BOOKMARKS)


class ChromiumReader(Reader):
   '''Profile reader for Chromium-based browsers'''
   def extensions(self):
      FILE = self.profile.path.joinpath(SECURE_PREFERENCES)

      with open(FILE) as f:
         data = json.load(f)

      # NOTE there is no schema version unfortunately

      for ext_id, ext in data['extensions']['settings'].items():
         # skip builtin components
         # https://chromium.googlesource.com/chromium/src/+/master/extensions/common/manifest.h#39
         if ext["location"] == 5:
            continue

         manifest = ext['manifest']

         # check manifest version (may be redundant)
         schema_version = manifest['manifest_version']
         if schema_version != 2:
            raise util.UnsupportedSchema(FILE, schema_version, 'extensions',
                                         'settings', ext_id, 'manifest')

         # get status (disabled/enabled)
         # https://chromium.googlesource.com/chromium/src/+/master/extensions/common/extension.h#51
         # https://bugs.chromium.org/p/chromium/issues/detail?id=794205
         # https://chromium.googlesource.com/chromium/src/+/master/extensions/browser/disable_reason.h#23
         disabled = ext.get('disable_reasons', 0)

         yield {
             'id':
             ext_id,
             'version':
             manifest['version'],
             'name':
             manifest['name'],
             'description':
             manifest['description'],
             'enabled':
             disabled == 0,
             'url':
             'https://chrome.google.com/webstore/detail/{}'.format(ext_id),
             'install_date':
             util.datetime_from_epoch(int(ext['install_time']), webkit=True),

             # NON CROSS-BROWSER DATA
             'extras': {
                 # NOTE author is in extras cause it's optional in the manifest
                 'author': manifest.get('author'),
                 'disable_reason': disabled,
                 'from_webstore': ext['from_webstore']
             }
         }

   def history(self):
      FILE = self.profile.path.joinpath(BOOKMARKS)
      db_bookmarks, db_version = self.open_database(FILE)

      if db_version[0] != 0:  # TODO
         raise util.UnsupportedSchema(FILE, db_version)

      cursor = db_bookmarks.cursor()
      cursor.execute(r'''SELECT title,
                         url,
                         visit_count,
                         last_visit_time
                         FROM urls WHERE hidden = 0
                         ORDER BY last_visit_time DESC''')

      for title, url, visit_count, last_visit_time in cursor.fetchall():
         yield {
             'url': url,
             'title': title,
             'visit_count': visit_count,
             'last_visit': util.datetime_from_epoch(last_visit_time,
                                                    webkit=True)
         }

   def bookmarks(self):
      raise NotImplementedError()

   def cookies(self):
      raise NotImplementedError()
