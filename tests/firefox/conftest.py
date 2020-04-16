# pylint: disable=unused-argument,redefined-outer-name

import os
from distutils import dir_util
from pathlib import Path

import pytest

from ..wrapper import FirefoxWrapper

DIR = Path(__file__).parent


@pytest.fixture
def profile(tmpdir, request):
   dir_util.copy_tree(os.path.join(DIR, 'profile'), str(tmpdir))

   return tmpdir


@pytest.fixture
def blank_profile(tmpdir, xvfb):
   FirefoxWrapper(tmpdir).start().stop()

   return tmpdir
