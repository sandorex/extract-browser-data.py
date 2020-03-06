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


class Reader(ABC):
   '''Base class for browser profile reader'''
   def __init__(self, profile: Profile):
      self.profile = profile

   def open_database(self, *path) -> Connection:
      '''Opens a database'''
      return util.open_database(self.profile.path.joinpaths(*path),
                                readonly=True)

   # ABSTRACT #
   @abstractmethod
   def extensions(self) -> t.Generator[t.Any, None, None]:
      '''Returns extensions installed by user'''
      raise NotImplementedError()

   @abstractmethod
   def history(self) -> t.Generator[t.Any, None, None]:
      '''Returns browsing history'''
      raise NotImplementedError()

   @abstractmethod
   def bookmarks(self) -> t.Generator[t.Any, None, None]:
      '''Returns bookmarks'''
      raise NotImplementedError()

   @abstractmethod
   def cookies(self) -> t.Generator[t.Any, None, None]:
      '''Returns cookies'''
      raise NotImplementedError()
