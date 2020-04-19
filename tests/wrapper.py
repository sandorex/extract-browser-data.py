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

import re
import subprocess
import time
from pathlib import Path

import autopy


class Wrapper:
   DEFAULT_EXECUTABLE_NAME: str

   def __init__(self, default_executable, executable, args):
      if executable is not None:
         self.executable = executable
      else:
         self.executable = default_executable

      self.args = args
      self.process = None

   def __enter__(self):
      return self.start()

   def __exit__(self, *args):
      self.stop()

   def start(self):
      self.process = subprocess.Popen([self.executable] + self.args)

      # delay for it to start properly
      time.sleep(6)
      return self

   def _stop(self):
      raise NotImplementedError()

   def stop(self):
      self._stop()

      self.process.wait(100)
      self.process = None

   def kill(self):
      self.process.kill()
      self.process.wait(100)
      self.process = None

   @classmethod
   def read_version(cls, executable=None):
      if executable is None:
         executable = cls.DEFAULT_EXECUTABLE_NAME

      try:
         version = subprocess.check_output(
             [executable, '--version'],
             stderr=subprocess.DEVNULL).decode('utf-8')
      except FileNotFoundError:
         return None

      match = re.search(r'([0-9.]+)', version)
      if match is None:
         return None

      version = match.group(1)

      # raw string version and a integer version
      return version, int(version.replace('.', ''))


# TODO read full version with build number (can be linux only, but if it does work on other platorms implement it)
class FirefoxWrapper(Wrapper):
   DEFAULT_EXECUTABLE_NAME: str = 'firefox'

   def __init__(self, profile, executable=None):
      self.profile_path = Path(profile).resolve().absolute()

      super().__init__(self.DEFAULT_EXECUTABLE_NAME, executable,
                       ['-profile', self.profile_path])

   def _stop(self):
      for i in range(3):
         autopy.key.tap('q', [autopy.key.Modifier.CONTROL])
         time.sleep(0.5)
         autopy.key.tap(autopy.key.Code.RETURN)
         time.sleep(1)


class ChromiumWrapper(Wrapper):
   DEFAULT_EXECUTABLE_NAME: str = 'chromium-browser'

   # TODO pass which keystore to use as an enum
   def __init__(self,
                user_data_dir,
                executable=None,
                use_basic_password_store=True):
      self.user_data_dir = Path(user_data_dir).resolve().absolute()

      args = [f'--user-data-dir={self.user_data_dir}']

      if use_basic_password_store:
         # NOTE any other password store will ask for a password
         args.append('--password-store=basic')

      super().__init__(self.DEFAULT_EXECUTABLE_NAME, executable,
                       ['--no-sandbox', '--disable-gpu'] + args)

   def _stop(self):
      autopy.key.tap('f', [autopy.key.Modifier.ALT])
      time.sleep(0.5)
      autopy.key.tap('x')
