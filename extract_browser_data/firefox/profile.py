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

from pathlib import Path
from typing import Union, Optional
from os.path import join as join_path, isfile as file_exists
from ..profile import Profile
from .reader import FirefoxReader
from .writer import FirefoxWriter
from .files import PLACES, COOKIES, EXTENSIONS
from . import functions as func


class FirefoxProfile(Profile):
   """Profile for Firefox-based browsers"""
   def __init__(self,
                name: Optional[str],
                path: Union[str, Path],
                default: bool = False):
      super().__init__(name, path, FirefoxReader, FirefoxWriter)

      self.default = default

   @staticmethod
   def is_valid_profile(path: Union[str, Path]) -> bool:
      # checking if any of the files does not exist
      for file in [PLACES, COOKIES, EXTENSIONS]:
         if not file_exists(join_path(path, file)):
            return False

      return True

   def is_profile_running(self) -> bool:
      return func.is_profile_running(self.path)
