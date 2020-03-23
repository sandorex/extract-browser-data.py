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

import os

from sqlite3 import Connection
from typing import Type, Union, Optional, List, Iterator, Any
from abc import ABC, abstractmethod
from pathlib import Path
from .common import Extension, Bookmark, URLVisit, Cookie
from . import util


class Profile(ABC):
   """Base browser profile class

   Attributes:
      name: Name of the profile
      path: Path to the profile
      reader_type: Reader class used to read from profile (must be a
         subclass of :class:`.reader.Reader`)
      writer_type: Writer class used to read from profile (must be a
         subclass of :class:`.writer.Writer`)

   Arguments:
      name: The name of the profile
      path: The path to the profile
      reader_type: Type that will be used as the reader, must be
         subclass of :class:`.reader.Reader`
      writer_type: Type that will be used as the writer, must be
         subclass of :class:`.writer.Writer`
   """
   def __init__(self, name: Optional[str], path: Union[str, Path],
                reader_type: Type['Reader'], writer_type: Type['Writer']):
      self.name = name
      self.path = Path(path)
      self.reader_type = reader_type
      self.writer_type = writer_type

   def reader(self) -> 'Reader':
      '''Tries to create a reader for the profile'''
      return self.reader_type(self)

   def writer(self) -> 'Writer':
      '''Tries to create a writer for the profile'''
      return self.writer_type(self)

   @staticmethod
   def find_compatible_profile(
       path: Union[str, Path]) -> Optional[Type['Profile']]:
      """Tries to find a compatible profile by going through subclasses of class
      :class:`Profile`

      Returns:
         ``None`` if a compatible class is not found
      """
      if not os.path.isdir(path):
         raise NotADirectoryError()

      c: 'Profile'
      for c in Profile.__subclasses__():
         if c.is_valid_profile(path):
            return c

      return None

   @staticmethod
   def open_profile(path: Union[str, Path]) -> Optional['Profile']:
      """Opens profile by using a compatible profile subclass (searches using
      :meth:`Profile.find_compatible_profile`)

      Returns ``None`` if no compatible profile is found
      """
      profile = Profile.find_compatible_profile(path)
      if profile is not None:
         return profile(None, path)  # type: ignore

      return None

   # ABSTRACT #
   @staticmethod
   @abstractmethod
   def is_valid_profile(path: Union[str, Path]) -> bool:
      '''Checks if profile exists at path'''
      raise NotImplementedError()

   @abstractmethod
   def is_profile_running(self) -> bool:
      '''Checks if a browser instance is running while using this profile'''
      raise NotImplementedError()


class Reader(ABC):
   """Base class for browser profile reader

   Arguments:
      profile: The profile to read from (must be a subclass of
         :class:`.profile.Profile`)
   """
   def __init__(self, profile: Profile) -> None:
      self.profile = profile

   def _open_database(
       self, *path: Union[str, Path]) -> Union[Connection, util.TempConnection]:
      '''Opens a sqlite3 database read-only relative to profile path'''

      return util.open_database(str(self.profile.path.joinpath(*path)),
                                readonly=True)

   # ABSTRACT #
   @abstractmethod
   def extensions(self) -> List[Extension]:
      """Gets extensions installed in the profile

      Returns:
         A list of :class:`.common.Extension`
      """
      raise NotImplementedError()

   @abstractmethod
   def history(self) -> Iterator[URLVisit]:
      """Gets browsing history

      Returns:
         A generator of :class:`.common.URLVisit`
      """
      raise NotImplementedError()

   @abstractmethod
   def bookmarks(self) -> Optional[Bookmark]:
      """Gets bookmarks

      Returns:
         :class:`.common.Bookmark`
      """
      raise NotImplementedError()

   @abstractmethod
   def cookies(self) -> Iterator[Cookie]:
      """Gets cookies

      Returns:
         A generator of :class:`.common.Cookie`
      """
      raise NotImplementedError()


class Writer(ABC):
   """Base class for browser profile writer

   Warning:
      A writer must be closed otherwise the databases may stay locked

   Tip:
      It's recommended to use this class as a context manager

   Arguments:
      profile (Profile): The profile to write to (must be a subclass of
         :class:`.profile.Profile`)
   """
   def __init__(self, profile: Profile) -> None:
      self.profile = profile

   def __enter__(self) -> 'Writer':
      self._open()
      return self

   def __exit__(self, *args: Any) -> None:
      self.close()

   def _open_database(self,
                      *path: str) -> Union[Connection, util.TempConnection]:
      '''Opens a database and locks it'''
      return util.open_database(self.profile.path.joinpath(*path), lock=True)

   # ABSTRACT #
   @abstractmethod
   def _open(self) -> None:
      '''Gets locks on required databases so it can write without
      interruptions'''
      raise NotImplementedError()

   @abstractmethod
   def close(self) -> None:
      '''Closes databases that were locked when opened'''
      raise NotImplementedError()

   @abstractmethod
   def write_history(self, history: Any, append: bool = False) -> None:
      '''TODO'''
      raise NotImplementedError()

   @abstractmethod
   def write_bookmarks(self, bookmarks: Any, append: bool = False) -> None:
      '''TODO'''
      raise NotImplementedError()

   @abstractmethod
   def write_cookies(self, cookies: Any, append: bool = False) -> None:
      '''TODO'''
      raise NotImplementedError()
