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

from os.path import join as join_path, isfile as file_exists
from .. import util
from ..reader import Reader
from ..common import Extension, URLVisit, Bookmark, Cookie
from .util import open_lz4, dt_from_epoch
from .files import (SESSIONSTORE, EXTENSIONS, PLACES, COOKIES, SIGNED_IN_USER,
                    CONTAINERS)


class FirefoxReader(Reader):
   '''Profile reader for Firefox-based browsers'''
   def _find_container(self, context_id):
      '''Finds container by the context id (returns context_id if it cannot be
      found)'''
      for container in self.containers():
         if container['id'] == context_id:
            return container

      return context_id

   # FIREFOX READER #
   def containers(self):
      """Returns firefox containers

      .. NOTICE::
         This function is Firefox only!
      """
      FILE = join_path(self.profile.path, CONTAINERS)

      if file_exists(FILE):
         yield
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

   def last_session(self):
      """Gets last session

      Yields nothing if firefox is running

      .. NOTICE::
         This function is Firefox only!
      """
      FILE = self.profile.path.joinpath(SESSIONSTORE)

      if not file_exists(FILE):
         yield
         return

      with open_lz4(FILE) as file:
         data = json.load(file)

      schema_version = data['version']
      if schema_version != ['sessionrestore', 1]:
         raise util.UnsupportedSchema(FILE, schema_version)

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

         yield tabs

   def account(self):
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
   def extensions(self):
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
         install_date = dt_from_epoch(extension['installDate'], 'milliseconds')
         last_update = dt_from_epoch(extension['updateDate'], 'milliseconds')

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

         extensions.append(
             Extension(
                 id=_id,
                 name=name,
                 version=extension['version'],
                 enabled=extension['active'],
                 description=description.strip(),
                 page_url=url,
                 install_date=install_date,

                 # extras
                 disabled_by_user=extension['userDisabled'],
                 author=author,
                 download_url=extension['sourceURI'],
                 last_update=last_update))

      return extensions

   def history(self):
      FILE = self.profile.path.joinpath(PLACES)
      db_places = self._open_database(FILE)
      db_version = util.read_database_version(db_places)

      if db_version != 53:
         raise util.UnsupportedSchema(FILE, db_version)

      with db_places:
         cursor = db_places.cursor()
         cursor.execute(r'''SELECT url, title, last_visit_date, visit_count
                            FROM moz_places
                            WHERE last_visit_date IS NOT NULL
                            ORDER BY last_visit_date DESC''')

         for url, title, last_visit, visit_count in cursor.fetchall():
            yield URLVisit(url, title, dt_from_epoch(last_visit,
                                                     'microseconds'),
                           visit_count)

   def bookmarks(self):
      FILE = self.profile.path.joinpath(PLACES)
      db_places = self._open_database(FILE)
      db_version = util.read_database_version(db_places)

      if db_version != 53:
         raise util.UnsupportedSchema(FILE, db_version)

      # NOTE separators are ignored cause they are not supported in chromium
      with db_places:
         cursor = db_places.cursor()
         # fetches only folders
         cursor.execute(r'''SELECT id,
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

         for _id, parent, title, date_added, last_modified in cursor.fetchall():
            bookmark = Bookmark.new_folder(
                title,
                dt_from_epoch(date_added, 'microseconds'), [],
                last_modified=dt_from_epoch(last_modified, 'microseconds'))

            folders[_id] = bookmark

            # id of 1 is the root folder
            if parent == 1:
               main_folders[_id] = bookmark
            else:
               folders[parent].children.append(bookmark)

         # fetches only bookmarks
         cursor.execute(r'''SELECT P.url,
                                   B.parent,
                                   B.title,
                                   B.dateAdded,
                                   B.lastModified
                            FROM moz_bookmarks B
                            JOIN moz_places P
                            WHERE B.fk IS P.id
                            AND B.type IS 1
                            ORDER BY B.lastModified DESC''')

         for url, parent, title, date_added, last_modified in cursor.fetchall():
            folder = folders[parent]
            folder.children.append(
                Bookmark.new(url,
                             title,
                             dt_from_epoch(date_added, 'microseconds'),
                             last_modified=dt_from_epoch(
                                 last_modified, 'microseconds')))

      toolbar = main_folders[3]
      other_bookmarks = main_folders[5]
      mobile = main_folders[6]

      # these are firefox only
      bookmarks_menu = main_folders[2]
      tags = main_folders[4]

      # NOTE when changing keep the order in sync with chromium/reader.py
      return Bookmark.new_folder(
          'root', 0, [toolbar, other_bookmarks, mobile, bookmarks_menu, tags])

   def cookies(self):
      FILE = self.profile.path.joinpath(COOKIES)
      db_cookies = self._open_database(FILE)
      db_version = util.read_database_version(db_cookies)

      if db_version != 10:
         raise util.UnsupportedSchema(FILE, db_version)

      with db_cookies:
         cursor = db_cookies.cursor()
         cursor.execute(r'''SELECT
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

         for base_domain, name, path, value, attributes, expiry, creation_time, last_accessed in cursor.fetchall(
         ):
            container = None
            if attributes:
               # NOTE this is the best way i've thought of to ensure that
               # attributes haven't changed..
               match = re.match(r'^\^userContextId=(\d+)$', attributes)
               if match is None:
                  raise RuntimeError(
                      f"invalid attributes found in cookie '{attributes}'")

               container = self._find_container(int(match.group(1)))

            yield Cookie(
                base_domain=base_domain,
                name=name,
                path=path,
                value=value,
                expiry=dt_from_epoch(expiry),
                date_added=dt_from_epoch(creation_time, 'microseconds'),
                last_accessed=dt_from_epoch(last_accessed, 'microseconds'),

                # extras
                container=container)
