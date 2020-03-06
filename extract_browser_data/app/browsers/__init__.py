'''Contains browser classes'''

from .browser import Browser
from .firefox import FirefoxBrowser
from .chromium import ChromiumBrowser
from .chromium_variants import *


def get_browsers(variants=True):
   '''Returns classes of supported browsers'''
   def get_all_subclasses(cls):
      return set(cls.__subclasses__()).union(
          [s for c in cls.__subclasses__() for s in get_all_subclasses(c)])

   if variants:
      return get_all_subclasses(Browser)

   return Browser.__subclasses__()
