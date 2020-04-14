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
'''Windows only functions used by both Firefox and Chromium browsers'''

import os
from pathlib import Path
from typing import Union

from .common import ProfileState


# pylint: disable=bare-except,no-member
def _is_lockfile_open(filepath: Union[str, Path]) -> bool:
   """Check if file is already opened in another process

   Notice:
      This function does not check if the path exists

   Warning:
      This function is windows only
   """
   # https://stackoverflow.com/a/37515805/6251201
   try:
      # open file cannot be renamed so it should throw something
      # it throws PermissionError with winerror = 32
      # (ERROR_SHARING_VIOLATION) but i don't don't think there is any need
      # for raising any other errors
      os.rename(filepath, filepath)
   except:
      return True
   return False


def read_profile_state_from_lockfile(path: Union[str, Path]) -> ProfileState:
   lockfile_path = Path(path)

   # if the lockfile doesn't exist it must be closed
   if not lockfile_path.exists():
      return ProfileState.CLOSED

   # if the lockfile is open then its running
   if _is_lockfile_open(lockfile_path):
      return ProfileState.RUNNING

   # any other case is unknown
   return ProfileState.UNKNOWN
