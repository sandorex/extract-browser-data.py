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

from os.path import isfile as file_exists
from os.path import join as join_path
from pathlib import Path
from typing import Optional, Union

from ..profile import Profile
from . import functions as func
from .files import (BOOKMARKS, COOKIES, HISTORY, LOGIN_DATA, PREFERENCES,
                    SECURE_PREFERENCES, WEB_DATA)
from .reader import ChromiumReader
from .writer import ChromiumWriter


class ChromiumProfile(Profile):
   """Profile for Chromium-based browsers"""
   def __init__(self, name: Optional[str], path: Union[str, Path]):
      super().__init__(name, path, ChromiumReader, ChromiumWriter)

   @classmethod
   def is_valid_profile(cls, path: Union[str, Path]) -> bool:
      # checking if any of the files does not exist
      for i in [
          PREFERENCES, HISTORY, LOGIN_DATA, WEB_DATA, COOKIES,
          SECURE_PREFERENCES, BOOKMARKS
      ]:
         if not file_exists(join_path(path, i)):
            return False

      return True

   def is_profile_running(self) -> bool:
      return func.is_profile_running(self.path)
