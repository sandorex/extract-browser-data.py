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
# pylint: disable=too-many-instance-attributes,too-many-arguments,too-few-public-methods

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ProfileState(Enum):
   '''Represents current state of the profile'''
   CLOSED = 1
   RUNNING = 2
   UNKNOWN = 3


class Extension:
   """Class that represents an extension

   Attributes:
      id: Extension id (differs between browsers)
      name: Extension name
      version: Extension version
      enabled: Is extension currently enabled
      description: Extension description
      addon_page: URL to page of the extension on the official store
      install_date: Extension install date
      extras: Data not available on all browsers
   """
   id: str
   name: str
   version: str
   enabled: bool
   description: str
   addon_page: str
   install_date: datetime
   extras: Dict[str, Any]

   def __init__(self, **kwargs: Any):
      args = [
          'id', 'name', 'version', 'enabled', 'description', 'addon_page',
          'install_date'
      ]

      self.extras = {}

      for i in args:
         setattr(self, i, kwargs[i])

      for k, v in kwargs.items():
         if k not in args:
            self.extras[k] = v

   def __str__(self) -> str:
      return "{} '{}' {}{}".format(self.id, self.name, self.version,
                                   ' disabled' if not self.enabled else '')


class URLVisit:
   """Class that represents a visit to a url

   Attributes:
      url: Url visited
      title: Title of the url visited (set by the website on load, may be equal
         to url)
      last_visit: Date last on which the url was last visited
      visit_count: Number of times the url was visited
      extras: Data that is not available on all browsers
   """
   def __init__(self, url: str, title: str, last_visit: datetime,
                visit_count: int, **extras: Dict[str, Any]):
      self.url = url
      self.title = title
      self.last_visit = last_visit
      self.visit_count = visit_count
      self.extras = extras

   def __str__(self) -> str:
      return "'{}' {}".format(self.title, self.url)


class Bookmark:
   """Bookmark class represents a bookmark or a bookmark folder

   Attributes:
      url: (None if folder) URL of the bookmark
      title: Title of the bookmark/folder
      date_added: Date when bookmark/folder was created
      children: (None if bookmark) Children inside of the folder
      extras: Bookmark data not available in all browsers
      is_folder: Whether or not the bookmark is a folder

   Notice:
      Use :fun:`Bookmark.new to create bookmarks and :fun:`Bookmark.new_folder`
      to create folders
   """
   def __init__(self, url: Optional[str], title: str, date_added: datetime,
                children: Optional[List['Bookmark']], **extras: Any):
      self.url = url
      self.title = title
      self.date_added = date_added
      self.children = children
      self.extras = extras

      self.is_folder: bool = self.children is not None

   def __str__(self) -> str:
      if self.is_folder:
         if self.title:
            result = "'{}' ".format(self.title)
         else:
            result = ""

         if self.children:
            return result + '[{} children]'.format(len(self.children))

         return result + '[]'

      return "'{}' {}".format(self.title, self.url)

   def flatten(self) -> List['Bookmark']:
      '''Flattens bookmarks in folder so that it results in a list of all
      bookmarks'''
      if not self.is_folder:
         # cannot flatten a non-folder bookmark
         return [self]

      bookmarks = []

      def recursive(b):  # type: ignore
         if b.is_folder:
            for i in b.children:
               recursive(i)
         else:
            bookmarks.append(b)

      recursive(self)

      return bookmarks

   @classmethod
   def new_folder(cls, title: str, date_added: datetime,
                  children: List['Bookmark'], **extras: Any) -> 'Bookmark':
      '''Creates a new folder'''
      return cls(None, title, date_added, children, **extras)

   @classmethod
   def new(cls, url: str, title: str, date_added: datetime,
           **extras: Any) -> 'Bookmark':
      '''Creates a new bookmark'''
      return cls(url, title, date_added, None, **extras)


class Cookie:
   """Cookie class, represents a single cookie for a domain

   Attributes:
      base_domain: Base domain which uses the cookie
      name: Name of the cookie
      path: Path of the cookie
      value: Value of the cookie
      expiry: Date when cookie expires
      date_added: Date when cookie was created
      last_accessed: Date when cookie was last accessed
      extras: Cookie data which isn't available on all browsers
   """
   base_domain: str
   name: str
   path: str
   value: str
   expiry: datetime
   date_added: datetime
   last_accessed: datetime
   extras: Dict[str, Any]

   __slots__ = [
       'base_domain', 'name', 'path', 'value', 'expiry', 'date_added',
       'last_accessed', 'extras'
   ]

   def __init__(self, **kwargs: Any) -> None:
      args = [
          'base_domain', 'name', 'path', 'value', 'expiry', 'date_added',
          'last_accessed'
      ]

      self.extras = {}

      for i in args:
         setattr(self, i, kwargs[i])

      for k, v in kwargs.items():
         if k not in args:
            self.extras[k] = v

   def __str__(self) -> str:
      return "{} {} {}".format(self.base_domain, self.path, self.name)
