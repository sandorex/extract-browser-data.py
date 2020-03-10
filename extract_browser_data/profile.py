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
from pathlib import Path


class Profile(ABC):
   """Base browser profile class"""
   def __init__(self, name, path, reader_type, writer_type):
      self.name = name
      self.path = Path(path)
      self.reader_type = reader_type
      self.writer_type = writer_type

   def reader(self, *args, **kwargs):
      '''Tries to create a reader for the profile'''
      return self.reader_type(self, *args, **kwargs)

   def writer(self, *args, **kwargs):
      '''Tries to create a writer for the profile'''
      return self.writer_type(self, *args, **kwargs)

   @staticmethod
   def find_compatible_profile(path):
      '''Finds a profile that is compatible for path'''
      for c in Profile.__subclasses__():
         if c.is_valid_profile(path):
            return c

      return None

   @staticmethod
   def open_profile(path, *args, **kwargs):
      """Opens profile, automatically finds a compatible profile class

      Returns ``None`` if no compatible profile is found
      """
      profile = Profile.find_compatible_profile(path)
      if profile is not None:
         return profile(None, path, *args, **kwargs)

      return None

   # ABSTRACT #
   @staticmethod
   @abstractmethod
   def is_valid_profile(path):
      '''Checks if profile exists at path'''
      raise NotImplementedError()

   @abstractmethod
   def is_profile_running(self):
      '''Checks if a browser instance is running while using this profile'''
      raise NotImplementedError()
