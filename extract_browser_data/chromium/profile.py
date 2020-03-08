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

from os.path import join as join_path, isfile as file_exists
from .. import util
from ..profile import Profile
from .reader import ChromiumReader
from .writer import ChromiumWriter
from .files import (PREFERENCES, HISTORY, LOGIN_DATA, WEB_DATA, COOKIES,
                    SECURE_PREFERENCES, BOOKMARKS)


class ChromiumProfile(Profile):
   """Profile for Chromium-based browsers"""
   def __init__(self, name: str, path: str):
      super().__init__(name, path, ChromiumReader, ChromiumWriter)

   @classmethod
   def is_valid_profile(cls, path: str) -> bool:
      # checking if any of the files does not exist
      # TODO untested!
      for i in [
          PREFERENCES, HISTORY, LOGIN_DATA, WEB_DATA, COOKIES,
          SECURE_PREFERENCES, BOOKMARKS
      ]:
         if not file_exists(join_path(path, i)):
            return False

      return True

   def is_profile_running(self) -> bool:
      # chromium locks databases when it's running, so i am using that
      # TODO untested!
      for file in [LOGIN_DATA, WEB_DATA, COOKIES]:
         if util.is_database_locked(util.open_database(
             self.path.joinpath(file))):
            return True

      return False
