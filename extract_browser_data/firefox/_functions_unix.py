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
'''Unix only functions for Firefox browser'''

import os
import errno

from pathlib import Path
from typing import Optional, Union
from .functions import ProfileState

LOCKFILE = 'lock'


def _is_process_running(pid: Union[str, int]) -> bool:
   """Check whether pid exists in the current process table

   Warning:
      This function is unix only
   """
   # https://stackoverflow.com/a/6940314/6251201

   pid = int(pid)

   if pid < 0:
      return False

   if pid == 0:
      # According to "man 2 kill" PID 0 refers to every process
      # in the process group of the calling process.
      # On certain systems 0 is a valid PID but we have no way
      # to know that in a portable fashion.
      raise ValueError('invalid PID 0')

   try:
      os.kill(pid, 0)
   except OSError as err:
      if err.errno == errno.ESRCH:
         # ESRCH == No such process
         return False

      if err.errno == errno.EPERM:
         # EPERM clearly means there's a process to deny access to
         return True

      # According to "man 2 kill" possible error values are
      # (EINVAL, EPERM, ESRCH)
      raise
   else:
      return True


def _read_pid_from_lockfile(path: Union[str, Path]) -> Optional[int]:
   '''Reads pid from firefox lockfile'''
   path = Path(path).joinpath(LOCKFILE)

   if path.is_symlink():
      link_target = os.readlink(path)

      try:
         return link_target[link_target.index(':') + 2:]
      except IndexError:
         pass

   return None


def read_profile_state(path: Union[str, Path]) -> ProfileState:
   path = Path(path)

   # if the lockfile does not exist then it's probably closed
   if not path.joinpath(LOCKFILE).is_symlink():
      return ProfileState.CLOSED

   # if the pid read is valid then it's running
   pid = _read_pid_from_lockfile(path)
   if pid is not None and _is_process_running(pid):
      return ProfileState.RUNNING

   # every other case is unknown
   return ProfileState.UNKNOWN
