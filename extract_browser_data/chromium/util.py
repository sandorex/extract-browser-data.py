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

import datetime


def dt_from_webkit_epoch(epoch):
   """Converts webkit format epoch into ``datetime``

   Returns
   =======
   Datetime unless epoch is None then it returns None

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

   if isinstance(epoch, str):
      epoch = int(epoch)

   return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=epoch)
