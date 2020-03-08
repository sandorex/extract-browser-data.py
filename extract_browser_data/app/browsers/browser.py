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
from os.path import expandvars, normpath
from abc import ABC, abstractmethod
from sys import platform

WIN32 = bool(platform in ['win32', 'cygwin'])
LINUX = bool(platform == 'linux')
MACOS = bool(platform == 'darwin')


class Browser(ABC):
   """Base browser class"""
   PROFILE_TYPE = None

   def __init__(self, data_path=None):
      if data_path is None:
         path = self.get_default_user_path()

         if WIN32:
            path = path[0]
         elif LINUX:
            path = path[1]
         elif MACOS:
            path = path[2]

         self.data_path = expandvars(normpath(path))
      else:
         self.data_path = data_path

      self.data_path = Path(self.data_path)

   def find_profile(self, profile_name):
      '''Tries to find a profile using the profile name, if it fails it returns
      `None`'''
      for profile in self.get_profiles():
         if profile.get_profile_name() == profile_name:
            return profile

      return None

   @classmethod
   def read_profile(cls, path):
      '''Reads a profile by path, returns `None` if the profile is invalid'''
      if not cls.is_valid_profile(path):
         return None

      return cls.PROFILE_TYPE(None, path, cls.get_browser_name())  # pylint: disable=not-callable

   @classmethod
   def is_valid_profile(cls, path):
      '''Checks if there is a valid profile at the path'''
      return cls.PROFILE_TYPE.is_valid_profile(path)

   # ABSTRACT #
   @classmethod
   @abstractmethod
   def get_default_user_path(cls):
      '''Returns default user data path for the browser'''
      raise NotImplementedError()

   @classmethod
   @abstractmethod
   def get_browser_name(cls):
      '''Returns browser name'''
      raise NotImplementedError()

   @abstractmethod
   def get_profiles(self):
      '''Returns all browser profiles'''
      raise NotImplementedError()
