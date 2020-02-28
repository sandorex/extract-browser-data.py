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


class Extension:
   '''Base class for browser extension'''
   def __init__(self, version, name, description, download_url, url,
                install_date, last_update):
      self.version = version
      self.name = name
      self.description = description
      self.download_url = download_url
      self.url = url
      self.install_date = install_date
      self.last_update = last_update

   def get_version(self):
      '''Get the version of the extension'''
      return self.version

   def get_name(self):
      '''Get name of the extension'''
      return self.name

   def get_description(self):
      '''Get the description of the extension'''
      return self.description

   def get_download_url(self):
      '''Get an url to download the same version of extension'''
      return self.download_url

   def get_url(self):
      '''Get an url to page of the extension (may not valid)'''
      return self.url

   def get_install_date(self):
      '''Get the date on which the extension was installed'''
      return self.install_date

   def get_last_update(self):
      '''Get the date on which the extension was last updated'''
      return self.last_update

   def __str__(self):
      return "Extension '{}' Version {}".format(self.name, self.version)


class Profile(ABC):
   """Base browser profile class

   `name` represents name of the profile
   `path` represents absolute path to the profile
   """
   def __init__(self, name, path, browser_name):
      self.name = name
      self.path = Path(path)
      self.browser_name = browser_name

   def get_profile_name(self):
      '''Returns name of the profile'''
      return self.name

   def get_profile_path(self):
      '''Returns absolute path to the profile directory'''
      return self.path

   def get_browser_name(self):
      '''Returns name of the browser that created the profile'''
      return self.browser_name

   def __str__(self):
      return "Profile {} at '{}'".format(self.name, self.path)

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
         self.user_data_path = Path(user_data_path)
      else:
         self.user_data_path = Path(self.get_default_user_data_path())

   def get_user_data_path(self):
      '''Returns user data path'''
      return self.user_data_path

   def find_profile(self, profile_name):
      '''Tries to find a browser profile using the profile name, if it fails it
      returns `None`'''
      for profile in self.get_profiles():
         if profile.get_profile_name() == profile_name:
            return profile

      return None

   def __str__(self):
      return "Browser '{}' with data path '{}'".format(self.get_browser_name(),
                                                       str(self.user_data_path))

   @classmethod
   def new(cls, user_data_path=None):
      '''Returns a new instance of browser using a different path'''
      return cls(user_data_path)

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
   def get_default_user_data_path(self):
      '''Returns default user data path for the browser'''
      raise NotImplementedError()
