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


class Profile(ABC):
   """Base browser profile class

   `name` represents name of the profile
   `path` represents absolute path to the profile
   """
   def __init__(self, name, path):
      self.name = name
      self.path = path

   def get_profile_name(self):
      '''Returns name of the profile'''
      return self.name

   def get_profile_path(self):
      '''Returns absolute path to the profile directory'''
      return self.path

   @abstractmethod
   def is_profile_running(self):
      '''Checks if a browser instance is running while using this profile'''
      raise NotImplementedError()

   @abstractmethod
   def get_extension_list(self):
      '''Returns list of extensions installed by user'''
      raise NotImplementedError()

   @abstractmethod
   def get_history(self):
      '''Returns browsing history'''
      raise NotImplementedError()

   @abstractmethod
   def get_bookmarks(self):
      '''Returns bookmarks'''
      raise NotImplementedError()

   @abstractmethod
   def get_autofill(self):
      '''Returns autofill data'''
      raise NotImplementedError()

   @abstractmethod
   def get_cookies(self):
      '''Returns autofill data'''
      raise NotImplementedError()


class Browser(ABC):
   """Base browser class

   if user_data_path is `None` output from `get_default_user_data_path()` will
   be used
   """
   def __init__(self, user_data_path=None):
      if user_data_path is not None:
         self.user_data_path = user_data_path
      else:
         self.user_data_path = self.get_default_user_data_path()

   def get_user_data_path(self):
      '''Returns user data path'''
      return self.user_data_path

   @abstractmethod
   def is_browser_running(self):
      """Checks if the browser is running

      It wont detect any instance of the browser, only if a browser that is
      using the specified user data directory is running
      """
      raise NotImplementedError()

   @abstractmethod
   def get_browser_name(self):
      '''Returns browser name'''
      raise NotImplementedError()

   @abstractmethod
   def get_profiles(self):
      '''Returns all browser profiles'''
      raise NotImplementedError()

   @abstractmethod
   def find_profile(self, profile_name):
      '''Tries to find a browser profile using the profile name, if it fails it
      returns `None`'''
      raise NotImplementedError()

   @abstractmethod
   def get_default_user_data_path(self):
      '''Returns default user data path for the browser'''
      raise NotImplementedError()
