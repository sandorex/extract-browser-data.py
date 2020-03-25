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

from typing import List, Iterator, Optional
from ..profile import Reader
from ..common import Extension, URLVisit, Bookmark, Cookie
from .files import (HISTORY, SECURE_PREFERENCES, BOOKMARKS, COOKIES)
from . import functions as func


class ChromiumReader(Reader):
   '''Profile reader for Chromium-based browsers'''
   def extensions(self) -> List[Extension]:
      return func.read_extensions(
          self.profile.path.joinpath(SECURE_PREFERENCES))

   def history(self) -> Iterator[URLVisit]:
      return func.read_history(self.profile.path.joinpath(HISTORY))

   def bookmarks(self) -> Optional[Bookmark]:
      return func.read_bookmarks(self.profile.path.joinpath(BOOKMARKS))

   def cookies(self) -> Iterator[Cookie]:
      return func.read_cookies(self.profile.path.joinpath(COOKIES))
