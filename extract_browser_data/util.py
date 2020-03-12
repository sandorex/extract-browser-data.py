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
   """Error caused when reading data with unsupported version

   Arguments:
      file (str): Path to the file where the unsupported version was found
      version: Version found in the file
      xpath (str): XPath to the version inside the file, used when reading json
         or any other data format to signify that it's not a version of the
         whole file but a section of it

   """
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
   """Reads version of database

   Uses ``PRAGMA user_version`` or meta table to extract database version

   Arguments:
      conn (sqlite3.Connection): Connection to a sqlite3 database
      use_meta (bool): Whether or not to use meta table to get the version

   Returns:
      If ``use_meta`` is true then it will return a tuple of
      ``version`` and ``last_supported_version`` otherwise it returns just
      ``version``

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
   """Checks is database locked

   Notice:
      This function may block for a while depending on timeout of the connection
   """
   try:
      conn.execute('PRAGMA user_version')
   except sqlite3.OperationalError as err:
      if str(err) == 'database is locked':
         return True

      raise err from None

   return False


class TempDatabase:
   """Wrapper around sqlite database and a tempfile

   Copies a database file into a tempfile and then opens it until it's closed
   then it deletes the tempfile and connection to the database

   Warning:
      The instance must be closed otherwise it will leave the tempfile undeleted
      with data read inside which may or may not be a security risk

   Arguments:
      path (str): Path to the database file
   """
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
   """Opens a sqlite database

   Arguments:
      path (str): Path to the database file
      readonly (bool): Should the database be open read-only
      copy_if_locked (bool): Should database be copied and then opened if it's
         locked (only in combination with ``readonly``)

   Returns:
      :class:`sqlite3.Connection` or if ``copy_if_locked`` is true then
      :class:`TempDatabase`
   """
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
