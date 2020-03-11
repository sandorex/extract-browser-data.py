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

from abc import ABC, abstractmethod
from . import util


class Reader(ABC):
   """Base class for browser profile reader

   Arguments:
      profile (Profile): The profile to read from (must be a subclass of
         :class:`.profile.Profile`)
   """
   def __init__(self, profile):
      self.profile = profile

   def _open_database(self, *path):
      '''Opens a sqlite3 database read-only'''
      return util.open_database(self.profile.path.joinpath(*path),
                                readonly=True,
                                copy_if_locked=True)

   # ABSTRACT #
   @abstractmethod
   def extensions(self):
      """Gets extensions installed in the profile

      Returns:
         A list of :class:`.common.Extension`
      """
      raise NotImplementedError()

   @abstractmethod
   def history(self):
      """Gets browsing history

      Returns:
         A generator of :class:`.common.URLVisit`
      """
      raise NotImplementedError()

   @abstractmethod
   def bookmarks(self):
      """Gets bookmarks

      Returns:
         A list of :class:`.common.Bookmark`
      """
      raise NotImplementedError()

   @abstractmethod
   def cookies(self):
      """Gets cookies

      Returns:
         A generator of :class:`.common.Cookie`
      """
      raise NotImplementedError()
