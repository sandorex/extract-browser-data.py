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
import re
import subprocess
import time
from pathlib import Path


def _get_window_id(pid):
   ids = subprocess.check_output(
       ['xdotool', 'search', '--onlyvisible', '--pid',
        str(pid)]).decode('utf-8').strip().split(' ')

   wid = None
   if len(ids) == 1:
      wid = ids[0]
   else:
      for window_id in ids:
         try:
            subprocess.check_call(['xdotool', 'getwindowname', window_id])
         except subprocess.CalledProcessError:
            continue

         wid = window_id
         break

   if wid is None:
      raise Exception('could not find the window id for Firefox')

   return wid


class Wrapper:
   DEFAULT_EXECUTABLE_NAME: str

   def __init__(self, default_executable, executable, args):
      self.executable = executable if executable is not None else default_executable
      self.args = args
      self.process = None
      self.wid = None

   def __enter__(self):
      return self.start()

   def __exit__(self, *args):
      self.stop()

   def start(self):
      self.process = subprocess.Popen([self.executable] + self.args)

      # delay for it to startup properly
      time.sleep(4)

      self.wid = _get_window_id(self.process.pid)
      return self

   def _stop(self):
      raise NotImplementedError()

   def stop(self):
      self._stop()

      self.process.wait(100)
      self.wid = None
      self.process = None

   def kill(self):
      self.process.kill()
      self.process.wait(100)
      self.process = None
      self.wid = None

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
      subprocess.check_call(['xdotool', 'windowactivate', '--sync', self.wid])
      time.sleep(0.5)
      subprocess.check_call(['wmctrl', '-ic', self.wid])
      time.sleep(0.5)
      subprocess.check_call(['xdotool', 'key', 'Return'])


# TODO pass which keystore to use as an enum


class ChromiumWrapper(Wrapper):
   DEFAULT_EXECUTABLE_NAME: str = 'chromium-browser'

   def __init__(self,
                user_data_dir,
                executable=None,
                additional_args=None,
                use_basic_password_store=True):
      self.user_data_dir = Path(user_data_dir).resolve().absolute()

      args = [f'--user-data-dir={self.user_data_dir}']

      if use_basic_password_store:
         # NOTE any other password store will ask for a password
         args.append('--password-store=basic')

      if additional_args is not None:
         args += additional_args

      super().__init__(self.DEFAULT_EXECUTABLE_NAME, executable,
                       ['--no-sandbox', '--disable-gpu'] + args)

   def _stop(self):
      subprocess.check_call(['xdotool', 'windowactivate', '--sync', self.wid])
      time.sleep(0.5)
      subprocess.check_call(['wmctrl', '-ic', self.wid])
