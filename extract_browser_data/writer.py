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

from sqlite3 import Connection

from .prelude import *
from .profile import Profile

# TODO class for history field
# TODO class for bookmark


class Writer(ABC):
   """Base class for browser profile writer

   .. NOTICE::
      Opening the files/databases should happend in ``open`` while closing
      should be implemented in ``close``
   """
   def __init__(self, profile: Profile):
      self.profile = profile

      self.open()

   def __exit__(self, *args):
      self.close()

   def open_database(self, *path) -> Connection:
      '''Opens a database and locks it'''
      conn = util.open_database(self.profile.path.joinpaths(*path))
      conn.execute('BEGIN EXCLUSIVE')

      return conn

   # ABSTRACT #
   @abstractmethod
   def open(self):
      '''Opens the writer (called by the constructor)'''
      raise NotImplementedError()

   @abstractmethod
   def close(self):
      '''Closes the writer'''
      raise NotImplementedError()

   @abstractmethod
   def write_history(self, history: t.Any, append: bool = False):
      '''Writes to history'''
      raise NotImplementedError()

   @abstractmethod
   def write_bookmarks(self, bookmarks: t.Any, append: bool = False):
      '''Writes to bookmarks'''
      raise NotImplementedError()

   @abstractmethod
   def write_cookies(self, cookies: t.Any, append: bool = False):
      '''Writes to cookies'''
      raise NotImplementedError()
