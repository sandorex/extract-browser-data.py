from setuptools import setup
from extract_browser_data import VERSION

setup(
   version = VERSION,
   name = 'extract-browser-data',
   description = 'Python utility to extract cookies, history, bookmarks from browsers.',
   url = 'https://github.com/sandorex/extract-browser-data.py',
   license = 'Apache',
   author = 'Sandorex',
   author_email = 'rzhw3h@gmail.com',

   entry_points = {
      'console_scripts': [
         'extract-browser-data=extract_browser_data.app.main:main',
         'extract-chromium-data=extract_browser_data.app.main:main_chromium',
         'extract-firefox-data=extract_browser_data.app.main:main_firefox',
      ]
   },

   packages = [ 'extract_browser_data' ],
   install_requires = [ x.strip() for x in open('requirements.txt').readlines() if x and not x.startswith('#') ],
   python_requires = '>=3.6'
)
