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

from typing import List, Iterator, Optional
from ..profile import Reader
from ..common import Extension, URLVisit, Bookmark, Cookie
from .. import util
from .util import dt_from_webkit_epoch
from .files import (HISTORY, SECURE_PREFERENCES, BOOKMARKS, COOKIES)


class ChromiumReader(Reader):
   '''Profile reader for Chromium-based browsers'''
   def extensions(self) -> List[Extension]:
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

         extensions.append(
             Extension(
                 id=ext_id,
                 name=manifest['name'],
                 version=manifest['version'],
                 enabled=disabled == 0,
                 description=manifest['description'],
                 page_url='https://chrome.google.com/webstore/detail/{}'.format(
                     ext_id),
                 install_date=dt_from_webkit_epoch(int(ext['install_time'])),

                 # extras
                 author=manifest.get('author'),
                 disable_reason=disabled,
                 from_webstore=ext['from_webstore']))

      return extensions

   def history(self) -> Iterator[URLVisit]:
      FILE = self.profile.path.joinpath(HISTORY)
      db_history = self._open_database(FILE)
      with db_history as conn:
         db_version, db_lsv = util.read_database_version(conn, use_meta=True)

         if db_lsv > 42:
            raise util.UnsupportedSchema(FILE, (db_version, db_lsv))

         cur = conn.execute(r'''SELECT title,
                                url,
                                visit_count,
                                last_visit_time
                                FROM urls WHERE hidden = 0
                                ORDER BY last_visit_time DESC''')

         for title, url, visit_count, last_visit_time in cur.fetchall():
            yield URLVisit(url, title, dt_from_webkit_epoch(last_visit_time),
                           visit_count)

   def bookmarks(self) -> Optional[Bookmark]:
      FILE = self.profile.path.joinpath(BOOKMARKS)

      if not FILE.is_file():
         return None

      with open(FILE) as f:
         data = json.load(f)

      schema_version = data['version']
      if schema_version != 1:
         raise util.UnsupportedSchema(FILE, schema_version)

      def recursive(bookmark):  # type: ignore
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

   def cookies(self) -> Iterator[Cookie]:
      FILE = self.profile.path.joinpath(COOKIES)
      db_history = self._open_database(FILE)
      with db_history as conn:
         db_version, db_lsv = util.read_database_version(conn, use_meta=True)

         if db_lsv > 12:
            raise util.UnsupportedSchema(FILE, (db_version, db_lsv))

         # TODO decrypt the cookie data

         cur = conn.execute(r'''SELECT name,
                                   host_key,
                                   value,
                                   path,
                                   expires_utc,
                                   creation_utc,
                                   last_access_utc
                                FROM cookies
                                ORDER BY last_access_utc DESC''')

         for i in cur.fetchall():
            yield Cookie(base_domain=i[1],
                         name=i[0],
                         path=i[3],
                         value=i[2],
                         expiry=dt_from_webkit_epoch(i[4]),
                         date_added=dt_from_webkit_epoch(i[5]),
                         last_accessed=dt_from_webkit_epoch(i[6]))
