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

from .chromium_reader import ChromiumReader
from .chromium_writer import ChromiumWriter
from ..profile import Profile
from ..prelude import *


class ChromiumProfile(Profile):
   """Profile for Chromium-based browsers"""
   def __init__(self, name: str, path: str):
      super().__init__(name, path, ChromiumReader, ChromiumWriter)

   @staticmethod
   def is_valid_profile(path: str) -> bool:
      raise NotImplementedError()

   def is_profile_running(self) -> bool:
      raise NotImplementedError()
