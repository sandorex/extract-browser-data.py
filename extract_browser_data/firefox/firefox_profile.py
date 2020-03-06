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

from .firefox_reader import FirefoxReader
from .firefox_writer import FirefoxWriter
from ..profile import Profile
from ..prelude import *

PROFILES = 'profiles.ini'
SESSIONSTORE = 'sessionstore.jsonlz4'
EXTENSIONS = 'extensions.json'
PLACES = 'places.sqlite'
COOKIES = 'cookies.sqlite'
SIGNED_IN_USER = 'signedInUser.json'
CONTAINERS = 'containers.json'


class FirefoxProfile(Profile):
   """Profile for Firefox-based browsers"""
   def __init__(self, name: str, path: str, default: bool):
      super().__init__(name, path, FirefoxReader, FirefoxWriter)

      self.default = default

   @staticmethod
   def is_valid_profile(path: str) -> bool:
      # checking if any of the files does not exist
      return not any(not file_exists(join_path(path, i))
                     for i in [PLACES, COOKIES, EXTENSIONS])

   def is_profile_running(self) -> bool:
      # firefox deletes 'sessionstore.jsonlz4' when it starts and it's created
      # again when it quits, so i am using it as a lockfile
      return not self.path.joinpath(SESSIONSTORE).is_file()
