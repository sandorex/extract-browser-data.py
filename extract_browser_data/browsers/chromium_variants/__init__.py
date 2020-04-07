'''Contains variants of chromium browser'''

from ... import util

from .brave import BraveBrowser

if util.platform() == util.Platform.WIN32:
   from .edge import EdgeBrowser
