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
# pylint: disable=missing-function-docstring

import json
import datetime
import re

from pathlib import Path
from typing import Dict, Iterator, Any, List, Optional, Union
from os.path import isfile as file_exists
from .. import util
from .util import dt_from_epoch, TimeUnit, open_lz4
from ..common import ProfileState, Extension, URLVisit, Bookmark, Cookie

# import platform specific functions
if util.platform() != util.Platform.WIN32:
   from ._functions_unix import read_profile_state  # pylint: disable=unused-import
# else:
#    from ._functions_win32 import read_profile_state # pylint: disable=unused-import


def is_profile_running(path: Union[str, Path]) -> bool:
   # unknown should be detected as running cause it may cause issues when the
   # data is modified after a crash
   return read_profile_state(path) != ProfileState.CLOSED


# FIREFOX #
def read_containers(file: Union[str, Path]) -> Iterator[Dict[str, Any]]:
   if not file_exists(file):
      yield
      return

   with open(file) as fd:
      data = json.load(fd)

   schema_version = data['version']
   if schema_version != 4:
      raise util.UnsupportedSchema(file, schema_version)

   for container in data['identities']:
      if container['public']:
         yield {
             'id': container['userContextId'],
             'name': container['name'],
             'icon': container['icon'],
             'color': container['color']
         }


# TODO if not at root of the profile it can also be found in sessionstore-backups/previous.jsonlz4, also check out sessionstore-backups/recovery.jsonlz4
# TODO make class for windows and tabs and also read on chromium
def read_last_session(
    file: Union[str, Path]) -> Optional[List[List[Dict[str, Any]]]]:
   if not file_exists(file):
      return None

   with open_lz4(file) as fd:
      data = json.load(fd)

   schema_version = data['version']
   if schema_version != ['sessionrestore', 1]:
      raise util.UnsupportedSchema(file, schema_version)

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
             'container': tab['userContextId'],
             'last-accessed': tab['lastAccessed']
         })

      windows.append(tabs)

   return windows


def read_account(file: Union[str, Path]) -> Optional[Dict[str, Any]]:
   if not file_exists(file):
      return None

   with open(file) as fd:
      data = json.load(fd)

   schema_version = data['version']
   if schema_version != 1:
      raise util.UnsupportedSchema(file, schema_version)

   data = data['accountData']['profileCache']['profile']

   return {
       'name': data['displayName'],
       'email': data['email'],
       'avatar': data['avatar']
   }


# CROSS-BROWSER #
def read_extensions(file: Union[str, Path]) -> List[Extension]:
   # NOTE utf8 encoding here is required
   with open(file, encoding='utf8') as fd:
      data = json.load(fd)

   # check schema version
   schema_version = data['schemaVersion']
   if schema_version != 31:
      raise util.UnsupportedSchema(file, schema_version)

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


def read_history(file: Union[str, Path]) -> Iterator[URLVisit]:
   with util.open_database(file, readonly=True) as conn:
      db_version = util.read_database_version(conn)[0]

      if db_version != 53:
         raise util.UnsupportedSchema(file, db_version)

      cur = conn.execute(r'''SELECT url, title, last_visit_date, visit_count
               FROM moz_places
               WHERE last_visit_date IS NOT NULL
               ORDER BY last_visit_date DESC''')

      for url, title, last_visit, visit_count in cur.fetchall():
         yield URLVisit(url, title,
                        dt_from_epoch(last_visit, TimeUnit.Microseconds),
                        visit_count)


def read_bookmarks(file: Union[str, Path]) -> Bookmark:
   with util.open_database(file, readonly=True) as conn:
      db_version = util.read_database_version(conn)[0]

      if db_version != 53:
         raise util.UnsupportedSchema(file, db_version)

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
             last_modified=dt_from_epoch(last_modified, TimeUnit.Microseconds))

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
                          last_modified=dt_from_epoch(last_modified,
                                                      TimeUnit.Microseconds)))

   toolbar = main_folders[3]
   other_bookmarks = main_folders[5]
   mobile = main_folders[6]

   # these are firefox only
   bookmarks_menu = main_folders[2]
   tags = main_folders[4]

   # NOTE when changing keep the order in sync with chromium/reader.py
   return Bookmark.new_folder(
       'root', datetime.datetime.now(),
       [toolbar, other_bookmarks, mobile, bookmarks_menu, tags])


def read_cookies(file: Union[str, Path]) -> Iterator[Cookie]:
   with util.open_database(file, readonly=True) as conn:
      db_version = util.read_database_version(conn)[0]

      if db_version != 10:
         raise util.UnsupportedSchema(file, db_version)

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

            container = match.group(1)

         yield Cookie(
             base_domain=base_domain,
             name=name,
             path=path,
             value=value,
             expiry=dt_from_epoch(expiry),
             date_added=dt_from_epoch(creation_time, TimeUnit.Microseconds),
             last_accessed=dt_from_epoch(last_accessed, TimeUnit.Microseconds),

             # extras
             container=container)
