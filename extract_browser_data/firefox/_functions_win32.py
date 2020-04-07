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
'''Windows only functions for Firefox browser'''

from pathlib import Path
from typing import Union
from .. import functions
from ..common import ProfileState
from .files import LOCKFILE_WIN32 as LOCKFILE


def read_profile_state(path: Union[str, Path]) -> ProfileState:
   return functions.read_profile_state_from_lockfile(Path(path) / LOCKFILE)
