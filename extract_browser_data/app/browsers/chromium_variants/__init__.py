'''Contains variants of chromium browser'''

from .. import prelude
from .brave import BraveBrowser

if prelude.WIN32:
   from .edge import EdgeBrowser
