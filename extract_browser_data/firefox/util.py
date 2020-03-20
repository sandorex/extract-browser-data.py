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

from datetime import datetime, timedelta
from enum import Enum
from typing import Union, BinaryIO
from pathlib import Path
from io import BytesIO
from lz4.block import decompress


def open_lz4(file: Union[str, Path]) -> BinaryIO:
   """Reads a mozilla lz4 file and decompresses it in memory while returning it
   as `BytesIO`
   """
   with open(file, 'rb') as fp:
      # read mozilla header
      # thanks to https://github.com/jscher2000/Firefox-File-Utilities
      header = fp.read(8)
      if header != b'mozLz40\0':
         raise RuntimeError(f'invalid header {header!r} for mozilla lz4 file')

      data = fp.read()

   return BytesIO(decompress(data))


class TimeUnit(Enum):
   '''Time units for use with :fun:`dt_from_epoch`'''
   Seconds = 'seconds'
   Milliseconds = 'milliseconds'
   Microseconds = 'microseconds'


def dt_from_epoch(epoch: int,
                  time_unit: TimeUnit = TimeUnit.Seconds) -> datetime:
   """Converts epoch into datetime using any time unit

   Arguments:
      epoch: Represents the time in time_unit
      time_unit: Time unit of epoch supplied

   Returns:
      Datetime unless epoch is None then it returns None
   """

   if epoch is None:
      return None

   return datetime(1970, 1, 1) + timedelta(**{time_unit.value: epoch})
