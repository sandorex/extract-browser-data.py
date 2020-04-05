from setuptools import find_packages, setup
from extract_browser_data import VERSION

setup(
    version=VERSION,
    name='extract-browser-data',
    description=
    'Python library and utility to extract cookies, history, bookmarks from browsers.',
    url='https://github.com/sandorex/extract-browser-data.py',
    license='Apache',
    author='Sandorex',
    author_email='rzhw3h@gmail.com',
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.6')
