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

# list that contains all supported browsers
BROWSERS = []


def register_browser(browser):
   '''Adds browser to the list of browsers'''
   BROWSERS.append(browser)


# these imports must be below both `register_browser` and `BROWSERS`
import extract_browser_data.browsers.firefox
import extract_browser_data.browsers.chromium.chromium
import extract_browser_data.browsers.chromium.brave
import extract_browser_data.browsers.chromium.edge
