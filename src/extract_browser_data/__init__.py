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
'''Library to extract data from browsers (only chromium and firefox based ones)
'''

__version__ = '0.1a0'
__author__ = 'Sandorex'
__email__ = 'rzhw3h@gmail.com'
__url__ = 'https://github.com/sandorex/extract-browser-data.py'
__license__ = "Apache2"
__copyright__ = "Copyright (c) 2020 Aleksandar Radivojevic"

from .chromium import ChromiumProfile
from .firefox import FirefoxProfile
from .profile import Profile
