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

import sqlite3


class UnsupportedSchema(RuntimeError):
   '''Error that is caused when trying to read data from an unsupported schema version'''
   def __init__(self, file, version):
      self.file = file
      self.version = version

      super().__init__("Unsupported schema version {} for file {}",
                       self.version, self.file)


def connect_readonly(path):
   '''Opens a sqlite database readonly'''
   return sqlite3.connect('file:{}?mode=ro'.format(path), uri=True)
