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

from typing import Any, Dict, Iterator, List, Optional

from ..common import Bookmark, Cookie, Extension, URLVisit
from ..profile import Reader
from . import functions as func
from .files import (CONTAINERS, COOKIES, EXTENSIONS, PLACES, SESSIONSTORE,
                    SIGNED_IN_USER)


class FirefoxReader(Reader):
   '''Profile reader for Firefox-based browsers'''
   def find_container(self, context_id: str) -> Optional[Dict[str, Any]]:
      '''Finds container by the context id (returns None if it cannot be found)
      '''
      return func.find_container(self.containers(), context_id)

   # FIREFOX READER #
   def containers(self) -> Iterator[Dict[str, Any]]:
      """Returns firefox containers

      Notice:
         This function is Firefox only!
      """

      return func.read_containers(self.profile.path.joinpath(CONTAINERS))

   def last_session(self) -> Optional[List[List[Dict[str, Any]]]]:
      """Gets last session

      Returns:
         Nothing if firefox is running otherwise list of windows with tabs

      Notice:
         This function is Firefox only!
      """
      return func.read_last_session(self.profile.path.joinpath(SESSIONSTORE))

   def account(self) -> Optional[Dict[str, Any]]:
      """Gets currently logged in account

      Returns:
         None if account is not logged in otherwise information about the user
         logged in

      Notice:
         This function is Firefox only!
      """
      return func.read_account(self.profile.path.joinpath(SIGNED_IN_USER))

   # READER #
   def extensions(self) -> List[Extension]:
      return func.read_extensions(self.profile.path.joinpath(EXTENSIONS))

   def history(self) -> Iterator[URLVisit]:
      return func.read_history(self.profile.path.joinpath(PLACES))

   def bookmarks(self) -> Bookmark:
      return func.read_bookmarks(self.profile.path.joinpath(PLACES))

   def cookies(self) -> Iterator[Cookie]:
      return func.read_cookies(self.profile.path.joinpath(COOKIES))
