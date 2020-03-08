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
import sqlite3
import tempfile
import shutil
import datetime


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


def read_database_version(conn):
   """Tries to read version from meta table if it fails reads PRAGMA
   user_version"""
   try:
      cur = conn.cursor()
      cur.execute('SELECT version, last_supported_version FROM meta')
      return cur.fetchone()
   except sqlite3.OperationalError as err:
      if str(err) == 'no such table: meta':
         cur.execute('PRAGMA user_version')
         return cur.fetchone()[0]

      raise err from None


def is_database_locked(conn):
   '''Checks if database is locked'''
   cur = conn.cursor()
   cur.execute(
       '''SELECT name FROM sqlite_master WHERE type='table' ORDER BY name''')

   try:
      cur.fetchone()
   except sqlite3.OperationalError as err:
      if str(err) == 'database is locked':
         return True

      raise err from None

   return False


class TempDatabase:
   '''Copies a file and opens it as a sqlite database'''
   def __init__(self, path: str):
      with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
         self.file_path = tmpfile.name

         with open(path, 'rb') as file:
            shutil.copyfileobj(file, tmpfile)

      self.conn = sqlite3.connect(self.file_path)

   def __enter__(self):
      return self.conn

   def __exit__(self, *args):
      self.close()

   def close(self):
      '''Closes the connection and deletes the tempfile'''
      self.conn.close()
      os.remove(self.file_path)


def open_database(path, readonly=False, copy_if_locked=False, lock=False):
   """TODO"""
   assert not (readonly and lock), 'cannot lock readonly database'

   if readonly:
      conn = sqlite3.connect('file:{}?mode=ro'.format(path), uri=True)

      if copy_if_locked and is_database_locked(conn):
         return TempDatabase(path)
   else:
      conn = sqlite3.connect(path)

      if lock:
         # lock for both read and write
         conn.execute('BEGIN EXCLUSIVE')

   return conn, read_database_version(conn)


def datetime_from_epoch(epoch: int,
                        time_unit: str = None,
                        webkit: bool = False) -> datetime.datetime:
   """Converts epoch into ``datetime``

   ``time_unit`` represents unit in which epoch is in

   ``webkit`` is epoch in webkit format

   Webkit Format
   =============

   This timestamp format is used in web browsers such as Apple Safari (WebKit),
   Google Chrome and Opera (Chromium/Blink). It's a 64-bit value for
   microseconds since Jan 1, 1601 00:00 UTC. One microsecond is one-millionth of
   a second.

   (https://www.epochconverter.com/webkit)
   """

   if epoch is None:
      return None

   if webkit:
      unit = 'microseconds'
      year_since = 1601
   else:
      year_since = 1970

   if time_unit is None:
      unit = 'seconds'
   else:
      unit = time_unit

   return datetime.datetime(year_since, 1,
                            1) + datetime.timedelta(**{unit: epoch})
