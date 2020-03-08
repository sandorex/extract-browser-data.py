'''Contains variants of chromium browser'''

from .. import browser

from .brave import BraveBrowser

if browser.WIN32:
   from .edge import EdgeBrowser
