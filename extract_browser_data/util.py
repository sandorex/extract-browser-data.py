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


class UnsupportedSchema(RuntimeError):
   '''Error that is caused when trying to read data from an unsupported schema
   version'''
   def __init__(self, file, version, *xpath):
      self.file = file
      self.version = version
      if len(xpath) > 0:
         self.xpath = '/' + '/'.join(xpath)
      else:
         self.xpath = None

      msg = "Unsupported schema version {} in file '{}'".format(
          self.version, self.file)

      if self.xpath is not None:
         msg += " at xpath '{}'".format(self.xpath)

      super().__init__(msg)


def read_database_version(conn, use_meta=False):
   """Reads database version

   Uses ``PRAGMA user_version`` by default, use ``use_meta`` to get version from
   meta table instead
   """
   cur = conn.cursor()

   if use_meta:
      cur = conn.cursor()
      cur.execute('SELECT key, value FROM meta')

      version = None
      last_compatible_version = None

      for key, value in cur.fetchall():
         if key == 'version':
            version = value

         if key == 'last_compatible_version':
            last_compatible_version = value

      return int(version), int(last_compatible_version)

   cur.execute('PRAGMA user_version')
   return cur.fetchone()[0]


def is_database_locked(conn):
   '''Checks if database is locked (may take a while if database timeout is
   long)'''
   try:
      conn.execute('PRAGMA user_version')
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
   assert not (readonly and lock), 'cannot lock a readonly database'

   if readonly:
      conn = sqlite3.connect('file:{}?mode=ro'.format(path), uri=True)

      if copy_if_locked and is_database_locked(conn):
         return TempDatabase(path)
   else:
      conn = sqlite3.connect(path)

      if lock:
         # lock for both read and write
         conn.execute('BEGIN EXCLUSIVE')

   return conn
