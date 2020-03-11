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
   def __init__(self, profile):
      self.profile = profile

   def __enter__(self):
      self._open()
      return self

   def __exit__(self, *args):
      self.close()

   def _open_database(self, *path):
      '''Opens a database and locks it'''
      return util.open_database(self.profile.path.joinpaths(*path), lock=True)

   # ABSTRACT #
   @abstractmethod
   def _open(self):
      '''Gets locks on required databases so it can write without
      interruptions'''
      raise NotImplementedError()

   @abstractmethod
   def close(self):
      '''Closes databases that were locked when opened'''
      raise NotImplementedError()

   @abstractmethod
   def write_history(self, history, append=False):
      '''TODO'''
      raise NotImplementedError()

   @abstractmethod
   def write_bookmarks(self, bookmarks, append=False):
      '''TODO'''
      raise NotImplementedError()

   @abstractmethod
   def write_cookies(self, cookies, append=False):
      '''TODO'''
      raise NotImplementedError()
