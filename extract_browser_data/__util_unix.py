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

import os
import errno

from typing import Union


def is_process_running(pid: Union[str, int]) -> bool:
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
