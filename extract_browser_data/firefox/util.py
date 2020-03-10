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

import datetime

from io import BytesIO
from lz4.block import decompress


def open_lz4(file):
   """Reads a mozilla lz4 file and decompressed it in memory while returning
   `BytesIO`
   """
   with open(file, 'rb') as fp:
      # read mozilla header
      # thanks to https://github.com/jscher2000/Firefox-File-Utilities
      header = fp.read(8)
      if header != b'mozLz40\0':
         raise RuntimeError(
             'invalid header {} for mozilla lz4 file'.format(header))

      data = fp.read()

   return BytesIO(decompress(data))


def dt_from_epoch(epoch, time_unit=None):
   """Converts epoch into datetime using any time unit

   Arguments
   =========

   epoch: int
      Represents the time in time_unit

   time_unit: str (defaults to seconds)
      Represents a time unit which epochi s represented in as a string
      (like seconds or microseconds)

   Returns
   =======

   Datetime unless epoch is None then it returns None
   """

   if epoch is None:
      return None

   if time_unit is None:
      unit = 'seconds'
   else:
      unit = time_unit

   return datetime.datetime(1970, 1, 1) + datetime.timedelta(**{unit: epoch})
