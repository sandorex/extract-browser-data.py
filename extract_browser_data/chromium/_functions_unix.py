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
'''Unix only functions for Chromium browser'''

import os

from pathlib import Path
from typing import Optional, Union
from .. import util
from .functions import ProfileState

LOCKFILE = 'SingletonLock'


def _read_pid_from_lockfile(path: Union[str, Path]) -> Optional[int]:
   '''Reads pid from chromium lockfile'''
   link_target = os.readlink(path)

   try:
      # the link points to 'HOSTNAME-PID'
      return link_target[link_target.index('-') + 1:]
   except IndexError:
      pass

   return None


def read_profile_state(path: Union[str, Path]) -> ProfileState:
   # the lockfile is in the data dir not the profile
   lockfile_path = Path(path).parent / LOCKFILE

   # if the lockfile does not exist then it's probably closed
   if not lockfile_path.is_symlink():
      return ProfileState.CLOSED

   # if the pid read is valid then it's running
   pid = _read_pid_from_lockfile(lockfile_path)
   if pid is not None and util.is_process_running(pid):
      return ProfileState.RUNNING

   # every other case is unknown
   return ProfileState.UNKNOWN
