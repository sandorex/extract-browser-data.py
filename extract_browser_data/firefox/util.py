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

from io import BytesIO
from lz4.block import decompress


def open_lz4_file(file):
   """Reads a mozilla lz4 file and decompressed it in memory while returning
   `BytesIO`
   """
   with open(file, 'rb') as fp:
      # read mozilla header
      # thanks to https://github.com/jscher2000/Firefox-File-Utilities
      header = fp.read(8)
      if header != b'mozLz40\0':
         raise RuntimeError(
             'mozilla lz4 file has invalid magic number {}'.format(header))

      data = fp.read()

   return BytesIO(decompress(data))
