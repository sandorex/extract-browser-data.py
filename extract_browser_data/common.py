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

import datetime


class Extension:
   '''TODO'''
   id: str
   name: str
   version: str
   enabled: bool
   description: str
   addon_page: str
   install_date: datetime.datetime

   def __init__(self, **kwargs):
      args = [
          'id', 'name', 'version', 'enabled', 'description', 'addon_page',
          'install_date'
      ]

      self.extras = []

      for i in args:
         setattr(self, i, kwargs[i])

      for k, v in kwargs.items():
         if k not in args:
            self.extras[k] = v

   def __str__(self):
      return "{} '{}' {}{}".format(self.id, self.name, self.version,
                                   ' disabled' if not self.enabled else '')


class URLVisit:
   '''TODO'''
   def __init__(self, url, title, last_visit, visit_count, **extras):
      self.url = url
      self.title = title
      self.last_visit = last_visit
      self.visit_count = visit_count
      self.extras = extras

   def __str__(self):
      return "'{}' {}".format(self.title, self.url)


class Bookmark:
   '''TODO'''
   def __init__(self, url, title, date_added, children, **extras):
      self.url = url
      self.title = title
      self.date_added = date_added
      self.children = children
      self.extras = extras

      self.is_folder = self.children is not None

   def __str__(self):
      if self.is_folder:
         if self.title:
            result = "'{}' ".format(self.title)
         else:
            result = ""

         if self.children:
            return result + '[{} children]'.format(len(self.children))

         return result + '[]'

      return "'{}' {}".format(self.title, self.url)

   def flatten(self):
      '''Flattens bookmarks in folder so that it results in a list of all
      bookmarks'''
      if not self.is_folder:
         # cannot flatten a non-folder bookmark
         return [self]

      bookmarks = []

      def recursive(b):
         if b.is_folder:
            for i in b.children:
               recursive(i)
         else:
            bookmarks.append(b)

      recursive(self)

      return bookmarks

   @classmethod
   def new_folder(cls, title, date_added, children, **extras):
      '''Creates a new folder'''
      return cls(None, title, date_added, children, **extras)

   @classmethod
   def new(cls, url, title, date_added, **extras):
      '''Creates a new bookmark'''
      return cls(url, title, date_added, None, **extras)


class Cookie:
   '''TODO'''
   base_domain: str
   name: str
   path: str
   value: str
   expiry: datetime.datetime
   date_added: datetime.datetime
   last_accessed: datetime.datetime

   def __init__(self, **kwargs):
      args = [
          'base_domain', 'name', 'path', 'value', 'expiry', 'date_added',
          'last_accessed'
      ]

      self.extras = []

      for i in args:
         setattr(self, i, kwargs[i])

      for k, v in kwargs.items():
         if k not in args:
            self.extras[k] = v

   def __str__(self):
      return "{} {} {}".format(self.base_domain, self.path, self.name)
