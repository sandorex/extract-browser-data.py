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
import sys
import sqlite3
import tempfile
import shutil

from enum import Enum
from sqlite3 import Connection
from pathlib import Path
from typing import Optional, Tuple, Union, Any


class Platform(Enum):
   '''Enum that represents the running platform'''
   UNKNOWN = 'unknown'
   WIN32 = 'win32'
   LINUX = 'linux'
   MACOS = 'darwin'

   @classmethod
   def _missing_(cls, _value):
      return cls.UNKNOWN


def platform() -> Platform:
   '''Returns the running platform'''
   return Platform(sys.platform)


class UnsupportedSchema(RuntimeError):
   """Error caused when reading data with unsupported version

   Arguments:
      file: Path to the file where the unsupported version was found
      version: Version found in the file
      xpath: XPath to the version inside the file, used when reading json
         or any other data format to signify that it's not a version of the
         whole file but a section of it

   """
   xpath: Optional[str]

   def __init__(self, file_path: Union[str, Path], version: Any,
                *xpath: str) -> None:
      self.file_path = Path(file_path)
      self.version = version
      if len(xpath) > 0:
         self.xpath = '/' + '/'.join(xpath)
      else:
         self.xpath = None

      msg = "Unsupported schema version {} in file '{}'".format(
          self.version, self.file_path)

      if self.xpath is not None:
         msg += " at xpath '{}'".format(self.xpath)

      super().__init__(msg)


def read_database_version(conn: Connection,
                          use_meta: bool = False) -> Tuple[int, int]:
   """Reads version of database

   Uses ``PRAGMA user_version`` or meta table to extract database version

   Arguments:
      conn: Connection to a sqlite3 database
      use_meta: Whether or not to use meta table to get the version

   Returns:
      If ``use_meta`` is true then it will return a tuple of
      ``version`` and ``last_supported_version`` otherwise it returns
      ``version`` twice as a tuple

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

      assert version is not None and last_compatible_version is not None

      return int(version), int(last_compatible_version)

   cur.execute('PRAGMA user_version')
   version = cur.fetchone()[0]

   return (version, version)


def is_database_locked(db: Union[str, Path]) -> bool:
   """Checks is database locked

   Notice:
      This function will block the thread for a while (the timeout is set to 0)
   """

   conn = sqlite3.connect(str(db), timeout=0)

   try:
      conn.execute('PRAGMA user_version')
   except sqlite3.OperationalError as err:
      if str(err) == 'database is locked':
         return True

      raise err from None

   return False


class TempConnection:
   """Wrapper around sqlite database and a tempfile

   Copies a database file into a tempfile and then opens it, when it's closed
   the tempfile is deleted and connection to the database is also closed

   Warning:
      The instance must be closed otherwise it will leave the tempfile undeleted
      with data inside which may or may not be a security risk

   Arguments:
      path: Path to the database file
   """
   def __init__(self, path: Union[str, Path]) -> None:
      with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
         self.file_path = tmpfile.name

         with open(path, 'rb') as file:
            shutil.copyfileobj(file, tmpfile)

      self.conn = sqlite3.connect(f'file:{self.file_path}?mode=ro', uri=True)

   def __enter__(self) -> Connection:
      return self.conn

   def __exit__(self, *args: Any) -> None:
      self.close()

   def close(self) -> None:
      '''Closes the connection and deletes the tempfile'''
      self.conn.close()
      os.remove(self.file_path)


def open_database(path: Union[str, Path],
                  readonly: bool = False,
                  lock: bool = False) -> Union[Connection, TempConnection]:
   """Opens a sqlite database (locked database will be copied to memory if
   readonly is true)

   Arguments:
      path: Path to the database file
      readonly: Should the database be open read-only

   Returns:
      Connection to :class:`sqlite3.Connection` or :class:`TempConnection` if
      the database is locked and ``readonly`` is true
   """
   assert not (readonly and lock), 'cannot lock a readonly database'

   if readonly:
      if is_database_locked(path):
         return TempConnection(path)

      conn = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
   else:
      # lock for both read and write
      conn = sqlite3.connect(path, isolation_level='EXCLUSIVE')

   return conn


# import os specific functions
if platform() != Platform.WIN32:
   from .__util_unix import is_process_running  # pylint: disable=unused-import
