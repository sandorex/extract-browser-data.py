# pylint: disable=unused-argument,redefined-outer-name

import os
from distutils import dir_util
from pathlib import Path

import pytest

from ..wrapper import ChromiumWrapper

DIR = Path(__file__).parent


@pytest.fixture
def profile(tmpdir, request):
   dir_util.copy_tree(os.path.join(DIR, 'user_data_dir'), str(tmpdir))

   # provide both the profile and the user_data_dir
   return tmpdir / 'Default', tmpdir


@pytest.fixture
def blank_profile(tmpdir, xvfb):
   ChromiumWrapper(tmpdir).start().stop()

   # provide both the profile and the user_data_dir
   return tmpdir / 'Default', tmpdir
