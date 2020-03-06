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

# TODO typing!!


class UnsupportedSchema(RuntimeError):
   '''Error that is caused when trying to read data from an unsupported schema
   version'''
   def __init__(self, file, version, *xpath):
      self.file = file
      self.version = version
      self.xpath = '/' + '/'.join(xpath)

      if xpath is None:
         msg = "Unsupported schema version {} for file '{}'".format(
             self.version, self.file)
      else:
         msg = "Unsupported schema version {} in file '{}' at xpath '{}'".format(
             self.version, self.file, self.xpath)

      super().__init__(msg)


def get_database_version(conn):
   '''Returns ``PRAGMA user_version`` from a sqlite database'''
   cursor = conn.cursor()
   cursor.execute('PRAGMA user_version')
   return cursor.fetchone()[0]


def open_database(path: str, readonly: bool = False) -> sqlite3.Connection:
   """Opens a sqlite database"""
   if readonly:
      return sqlite3.connect('file:{}?mode=ro'.format(path), uri=True)

   return sqlite3.connect(path)
