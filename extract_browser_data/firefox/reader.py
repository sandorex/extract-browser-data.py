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
import re

from datetime import datetime
from typing import Dict, Iterator, Any, List, Optional
from os.path import isfile as file_exists
from .. import util
from ..profile import Reader
from ..common import Extension, URLVisit, Bookmark, Cookie
from .util import open_lz4, dt_from_epoch, TimeUnit
from .files import (SESSIONSTORE, EXTENSIONS, PLACES, COOKIES, SIGNED_IN_USER,
                    CONTAINERS)


class FirefoxReader(Reader):
   '''Profile reader for Firefox-based browsers'''
   def _find_container(self, context_id: str) -> Optional[Dict[str, Any]]:
      '''Finds container by the context id (returns None if it cannot be found)
      '''
      for container in self.containers():
         if container['id'] == context_id:
            return container

      return None

   # FIREFOX READER #
   def containers(self) -> Iterator[Dict[str, Any]]:
      """Returns firefox containers

      .. NOTICE::
         This function is Firefox only!
      """
      FILE = self.profile.path.joinpath(CONTAINERS)

      if not file_exists(FILE):
         return

      with open(FILE) as file:
         data = json.load(file)

      schema_version = data['version']
      if schema_version != 4:
         raise util.UnsupportedSchema(FILE, schema_version)

      for container in data['identities']:
         if container['public']:
            yield {
                'id': container['userContextId'],
                'name': container['name'],
                'icon': container['icon'],
                'color': container['color']
            }

   def last_session(self) -> Optional[List[List[Dict[str, Any]]]]:
      """Gets last session

      Yields nothing if firefox is running

      .. NOTICE::
         This function is Firefox only!
      """
      FILE = self.profile.path.joinpath(SESSIONSTORE)

      if not file_exists(FILE):
         return None

      with open_lz4(FILE) as file:
         data = json.load(file)

      schema_version = data['version']
      if schema_version != ['sessionrestore', 1]:
         raise util.UnsupportedSchema(FILE, schema_version)

      windows = []
      for window in data['windows']:
         tabs = []
         for tab in window['tabs']:
            # current entry in the tab, others are history
            current_entry = tab['entries'][0]

            tabs.append({
                'index': tab['index'],
                'title': current_entry['title'],
                'url': current_entry['url'],
                'container': self._find_container(tab['userContextId']),
                'last-accessed': tab['lastAccessed']
            })

         windows.append(tabs)

      return windows

   def account(self) -> Optional[Dict[str, Any]]:
      """Gets currently logged in account

      Returns ``None`` if account is not logged in

      .. NOTICE::
         This function is Firefox only!
      """
      FILE = self.profile.path.joinpath(SIGNED_IN_USER)

      if not file_exists(FILE):
         return None

      with open(FILE) as file:
         data = json.load(file)

      schema_version = data['version']
      if schema_version != 1:
         raise util.UnsupportedSchema(FILE, schema_version)

      data = data['accountData']['profileCache']['profile']

      return {
          'name': data['displayName'],
          'email': data['email'],
          'avatar': data['avatar']
      }

   # READER #
   def extensions(self) -> List[Extension]:
      FILE = self.profile.path.joinpath(EXTENSIONS)

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

         # both installDate and updateDate are in milliseconds since epoch
         install_date = dt_from_epoch(extension['installDate'],
                                      TimeUnit.Milliseconds)
         last_update = dt_from_epoch(extension['updateDate'],
                                     TimeUnit.Milliseconds)

         _id = extension['id']

         # mozilla.org redirects to the page of the addon when id is supplied
         url = 'https://addons.mozilla.org/en-US/firefox/addon/{}/'.format(_id)

         name = None
         description = None
         author = None

         # find english locale
         for locale in extension['locales']:
            if 'en' in locale['locales']:
               name = locale.get('name')
               description = locale.get('description')
               author = locale.get('creator')

         # fallback
         if any(x is None for x in [name, description, author]):
            name = extension["defaultLocale"]['name']
            description = extension["defaultLocale"]['description']
            author = extension["defaultLocale"]['creator']

         # TODO ensure name, description and auther is not None

         extensions.append(
             Extension(
                 id=_id,
                 name=name,
                 version=extension['version'],
                 enabled=extension['active'],
                 description=description.strip(),  # type: ignore
                 page_url=url,
                 install_date=install_date,

                 # extras
                 disabled_by_user=extension['userDisabled'],
                 author=author,
                 download_url=extension['sourceURI'],
                 last_update=last_update))

      return extensions

   def history(self) -> Iterator[URLVisit]:
      FILE = self.profile.path.joinpath(PLACES)
      db_places = self._open_database(FILE)

      with db_places as conn:
         db_version = util.read_database_version(conn)[0]

         if db_version != 53:
            raise util.UnsupportedSchema(FILE, db_version)

         cur = conn.execute(r'''SELECT url, title, last_visit_date, visit_count
                 FROM moz_places
                 WHERE last_visit_date IS NOT NULL
                 ORDER BY last_visit_date DESC''')

         for url, title, last_visit, visit_count in cur.fetchall():
            yield URLVisit(url, title,
                           dt_from_epoch(last_visit, TimeUnit.Microseconds),
                           visit_count)

   def bookmarks(self) -> Bookmark:
      FILE = self.profile.path.joinpath(PLACES)
      db_places = self._open_database(FILE)
      with db_places as conn:
         db_version = util.read_database_version(conn)[0]

         if db_version != 53:
            raise util.UnsupportedSchema(FILE, db_version)

         cur = conn.cursor()

         # NOTE separators are ignored cause they are not supported in chromium
         # fetches only folders
         cur.execute(r'''SELECT id,
                                   parent,
                                   title,
                                   dateAdded,
                                   lastModified
                            FROM moz_bookmarks
                            WHERE type IS 2
							       AND id IS NOT 1
                            ORDER BY id ASC''')

         main_folders = {}
         folders = {}

         for _id, parent, title, date_added, last_modified in cur.fetchall():
            bookmark = Bookmark.new_folder(
                title,
                dt_from_epoch(date_added, TimeUnit.Microseconds), [],
                last_modified=dt_from_epoch(last_modified,
                                            TimeUnit.Microseconds))

            folders[_id] = bookmark

            # id of 1 is the root folder
            if parent == 1:
               main_folders[_id] = bookmark
            else:
               folders[parent].children.append(bookmark)  # type: ignore

         # fetches only bookmarks
         cur.execute(r'''SELECT P.url,
                                   B.parent,
                                   B.title,
                                   B.dateAdded,
                                   B.lastModified
                            FROM moz_bookmarks B
                            JOIN moz_places P
                            WHERE B.fk IS P.id
                            AND B.type IS 1
                            ORDER BY B.lastModified DESC''')

         for url, parent, title, date_added, last_modified in cur.fetchall():
            folder = folders[parent]
            folder.children.append(  # type: ignore
                Bookmark.new(url,
                             title,
                             dt_from_epoch(date_added, TimeUnit.Microseconds),
                             last_modified=dt_from_epoch(
                                 last_modified, TimeUnit.Microseconds)))

      toolbar = main_folders[3]
      other_bookmarks = main_folders[5]
      mobile = main_folders[6]

      # these are firefox only
      bookmarks_menu = main_folders[2]
      tags = main_folders[4]

      # NOTE when changing keep the order in sync with chromium/reader.py
      return Bookmark.new_folder(
          'root', datetime.now(),
          [toolbar, other_bookmarks, mobile, bookmarks_menu, tags])

   def cookies(self) -> Iterator[Cookie]:
      FILE = self.profile.path.joinpath(COOKIES)
      db_cookies = self._open_database(FILE)
      with db_cookies as conn:
         db_version = util.read_database_version(conn)[0]

         if db_version != 10:
            raise util.UnsupportedSchema(FILE, db_version)

         cur = conn.execute(r'''SELECT
                              baseDomain,
                              name,
                              path,
                              value,
                              originAttributes,
                              expiry,
                              creationTime,
                              lastAccessed
                              FROM moz_cookies
                              ORDER BY lastAccessed DESC''')

         for (base_domain, name, path, value, attributes, expiry, creation_time,
              last_accessed) in cur.fetchall():
            container = None
            if attributes:
               # NOTE this is the best way i've thought of to ensure that
               # attributes haven't changed..
               match = re.match(r'^\^userContextId=(\d+)$', attributes)
               if match is None:
                  raise RuntimeError(
                      f"invalid attributes found in cookie '{attributes}'")

               container = self._find_container(match.group(1))

            yield Cookie(
                base_domain=base_domain,
                name=name,
                path=path,
                value=value,
                expiry=dt_from_epoch(expiry),
                date_added=dt_from_epoch(creation_time, TimeUnit.Microseconds),
                last_accessed=dt_from_epoch(last_accessed,
                                            TimeUnit.Microseconds),

                # extras
                container=container)
