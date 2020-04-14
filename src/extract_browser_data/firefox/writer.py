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

from abc import abstractmethod

from ..profile import Writer


class FirefoxWriter(Writer):
   """Profile writer for Firefox-based browsers"""
   @abstractmethod
   def open(self) -> 'FirefoxWriter':
      raise NotImplementedError()

   @abstractmethod
   def close(self):
      raise NotImplementedError()

   @abstractmethod
   def write_history(self, history, append=False):
      raise NotImplementedError()

   @abstractmethod
   def write_bookmarks(self, bookmarks, append=False):
      raise NotImplementedError()

   @abstractmethod
   def write_cookies(self, cookies, append=False):
      raise NotImplementedError()
