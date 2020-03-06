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

from .prelude import *


class Profile(ABC):
   """Base browser profile class"""
   def __init__(self, name: str, path: str, reader_type: t.Type,
                writer_type: t.Type):
      self.name = name
      self.path = Path(path)
      self.reader_type = reader_type
      self.writer_type = writer_type

   def reader(self, *args, **kwargs) -> t.Type:
      '''Tries to create a reader for the profile'''
      return self.reader_type(self, *args, **kwargs)

   def writer(self, *args, **kwargs) -> t.Type:
      '''Tries to create a writer for the profile'''
      return self.writer_type(self, *args, **kwargs)

   # ABSTRACT #
   @staticmethod
   @abstractmethod
   def is_valid_profile(path: str) -> bool:
      '''Checks if profile exists at path'''
      raise NotImplementedError()

   @abstractmethod
   def is_profile_running(self) -> bool:
      '''Checks if a browser instance is running while using this profile'''
      raise NotImplementedError()
