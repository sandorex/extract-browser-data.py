import codecs
import os
import re

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
   """
   Build an absolute path from *parts* and and return the contents of the
   resulting file.  Assume UTF-8 encoding.
   """
   with codecs.open(os.path.join(HERE, *parts), 'rb', 'utf-8') as f:
      return f.read()


META_FILE = read('src', 'extract_browser_data', '__init__.py')


def find_meta(meta):
   """
   Extract __*meta*__ from META_FILE.
   """
   meta_match = re.search(
       r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta), META_FILE, re.M)
   if meta_match:
      return meta_match.group(1)

   raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


setup(
    version=find_meta('version'),
    name='extract-browser-data',
    description=
    'Python library and utility to extract cookies, history, bookmarks from browsers.',
    long_description=read('README.rst'),
    url='https://github.com/sandorex/extract-browser-data.py',
    license=find_meta('license'),
    author=find_meta('author'),
    author_email=find_meta('email'),
    maintainer=find_meta('author'),
    maintainer_email=find_meta('email'),
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=read('requirements.txt'),
    python_requires='>=3.6')
