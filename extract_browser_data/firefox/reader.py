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
from .util import open_lz4_file
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
                'id': self._find_container(
                    container['userContextId']),  # TODO get container
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

      with open_lz4_file(FILE) as file:
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

      for extension in data['addons']:
         # skip themes and such
         if extension["type"] != "extension":
            continue

         # skip builtin extensions
         if extension["location"] != "app-profile":
            continue

         # both installDate and updateDate are in milliseconds since epoch
         install_date = util.datetime_from_epoch(extension['installDate'],
                                                 'milliseconds')
         last_update = util.datetime_from_epoch(extension['updateDate'],
                                                'milliseconds')

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

         # BUG sometimes author is None
         yield {
             'id': _id,
             'version': extension['version'],
             'name': name,
             'description': description.strip(),
             'enabled': True,  # TODO check if it's possible to read from files
             'url': url,
             'install_date': install_date,

             # NON CROSS-BROWSER DATA
             'extras': {
                 'author': author,
                 'download_url': extension['sourceURI'],
                 'last_update': last_update
             }
         }

   def history(self):
      FILE = self.profile.path.joinpath(PLACES)
      db_places, db_version = self.open_database(FILE)

      if db_version != 53:
         raise util.UnsupportedSchema(FILE, db_version)

      with db_places:
         # TODO get contextId
         cursor = db_places.cursor()
         cursor.execute(r'''SELECT url, title, last_visit_date
                              FROM moz_places
                              WHERE last_visit_date IS NOT NULL
                              ORDER BY last_visit_date DESC''')

         for url, title, last_visit in cursor.fetchall():
            yield {
                'url': url,
                'title': title,
                # time is in microseconds since epoch
                'last_visit': util.datetime_from_epoch(last_visit,
                                                       'microseconds')
            }

   def bookmarks(self):
      FILE = self.profile.path.joinpath(PLACES)
      db_places, db_version = self.open_database(FILE)

      if db_version != 53:
         raise util.UnsupportedSchema(FILE, db_version)

      with db_places:
         cursor = db_places.cursor()
         cursor.execute(r'''SELECT P.url,
                                    B.id,
                                    B.parent,
                                    B.title,
                                    B.dateAdded,
                                    B.lastModified
                              FROM moz_bookmarks B
                              JOIN moz_places P
                              WHERE B.fk == P.id
                              ORDER BY B.lastModified DESC''')

         # TODO get the folder hiarcharchy
         # TODO make Bookmark class

         for url, _id, parent, title, date_added, last_modified in cursor.fetchall(
         ):
            yield {
                'url':
                url,
                'id':
                _id,
                'parent':
                parent,
                'title':
                title,
                # time is in microseconds since epoch
                'date_added':
                util.datetime_from_epoch(date_added, 'microseconds'),
                'last_modified':
                util.datetime_from_epoch(last_modified, 'microseconds')
            }

   def cookies(self):
      FILE = self.profile.path.joinpath(COOKIES)
      db_cookies, db_version = self.open_database(FILE)

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

            yield {
                'base-domain':
                base_domain,
                'name':
                name,
                'path':
                path,
                'value':
                value,
                'container':
                container,
                # time is in seconds since epoch
                'expiry':
                util.datetime_from_epoch(expiry),
                # both creationTime and lastAccessed are in microseconds since epoch
                'creation-time':
                util.datetime_from_epoch(creation_time, 'microseconds'),
                'last-accessed':
                util.datetime_from_epoch(last_accessed, 'microseconds')
            }
