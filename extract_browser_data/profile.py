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
   """Base browser profile class

   Attributes:
      name (str): Name of the profile
      path (Path): Path to the profile
      reader_type (type): Reader class used to read from profile (must be a
         subclass of :class:`.reader.Reader`)
      writer_type (type): Writer class used to read from profile (must be a
         subclass of :class:`.writer.Writer`)

   Arguments:
      name (str): The name of the profile
      path (str or Path): The path to the profile
      reader_type (type): Type that will be used as the reader, must be
         subclass of :class:`.reader.Reader`
      writer_type (type): Type that will be used as the writer, must be
         subclass of :class:`.writer.Writer`
   """
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
      """Tries to find a compatible profile by going through subclasses of class
      :class:`Profile`

      Returns:
         ``None`` if a compatible class is not found
      """
      for c in Profile.__subclasses__():
         if c.is_valid_profile(path):
            return c

      return None

   @staticmethod
   def open_profile(path, *args, **kwargs):
      """Opens profile by using a compatible profile subclass (searches using
      :meth:`Profile.find_compatible_profile`)

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
