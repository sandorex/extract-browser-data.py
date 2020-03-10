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
from ..common import Extension, URLVisit, Bookmark
from .. import util
from .util import dt_from_webkit_epoch
from .files import (HISTORY, SECURE_PREFERENCES, BOOKMARKS)


class ChromiumReader(Reader):
   '''Profile reader for Chromium-based browsers'''
   def extensions(self):
      FILE = self.profile.path.joinpath(SECURE_PREFERENCES)

      with open(FILE) as f:
         data = json.load(f)

      # NOTE there is no schema version unfortunately

      extensions = []
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

         extras = {
             'author': manifest.get('author'),
             'disable_reason': disabled,
             'from_webstore': ext['from_webstore']
         }

         extensions.append(
             Extension(
                 ext_id, manifest['name'], manifest['version'], disabled == 0,
                 manifest['description'],
                 'https://chrome.google.com/webstore/detail/{}'.format(ext_id),
                 dt_from_webkit_epoch(int(ext['install_time'])), **extras))

      return extensions

   def history(self):
      FILE = self.profile.path.joinpath(HISTORY)
      db_history = self.open_database(FILE)
      db_version, db_lsv = util.read_database_version(db_history, use_meta=True)

      if db_lsv > 42:
         raise util.UnsupportedSchema(FILE, db_version)

      with db_history:
         cursor = db_history.cursor()
         cursor.execute(r'''SELECT title,
                           url,
                           visit_count,
                           last_visit_time
                           FROM urls WHERE hidden = 0
                           ORDER BY last_visit_time DESC''')

         for title, url, visit_count, last_visit_time in cursor.fetchall():
            yield URLVisit(url, title, dt_from_webkit_epoch(last_visit_time),
                           visit_count)

   def bookmarks(self):
      FILE = self.profile.path.joinpath(BOOKMARKS)

      if not FILE.is_file():
         return None

      with open(FILE) as f:
         data = json.load(f)

      schema_version = data['version']
      if schema_version != 1:
         raise util.UnsupportedSchema(FILE, schema_version)

      def recursive(bookmark):
         title = bookmark['name']
         date_added = dt_from_webkit_epoch(bookmark['date_added'])

         if bookmark['type'] == 'folder':
            return Bookmark.new_folder(
                title,
                date_added, [recursive(i) for i in bookmark['children']],
                date_modified=dt_from_webkit_epoch(bookmark['date_modified']))

         return Bookmark.new(bookmark['url'], title, date_added)

      roots = data['roots']

      toolbar = recursive(roots['bookmark_bar'])
      other = recursive(roots['other'])
      synced = recursive(roots['synced'])

      # NOTE when changing keep the order in sync with firefox/reader.py
      return Bookmark.new_folder('root', 0, [toolbar, other, synced])

   def cookies(self):
      raise NotImplementedError()
