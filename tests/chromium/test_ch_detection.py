# pylint: disable=unused-argument

import pytest

import extract_browser_data as ebd
import extract_browser_data.chromium.functions as func

from ..wrapper import ChromiumWrapper

pytestmark = pytest.mark.gui

PROFILE_NAME = 'Default'


def test_ch_running(xvfb, tmpdir, request):
   with ChromiumWrapper(tmpdir,
                        executable=request.config.getoption("--chromium")):

      profile = tmpdir / PROFILE_NAME
      assert func.read_profile_state(profile) == func.ProfileState.RUNNING
      assert ebd.ChromiumProfile(None, profile).is_profile_running()


def test_ch_not_running(xvfb, tmpdir, request):
   # start and stop chromium
   ChromiumWrapper(
       tmpdir,
       executable=request.config.getoption("--chromium")).start().stop()

   profile = tmpdir / PROFILE_NAME
   assert func.read_profile_state(profile) == func.ProfileState.CLOSED
   assert not ebd.ChromiumProfile(None, profile).is_profile_running()


def test_ch_crashed(xvfb, tmpdir, request):
   # start and kill chromium
   ChromiumWrapper(
       tmpdir,
       executable=request.config.getoption("--chromium")).start().kill()

   profile = tmpdir / PROFILE_NAME
   assert func.read_profile_state(profile) == func.ProfileState.UNKNOWN

   # it should be detected as if it was running
   assert ebd.ChromiumProfile(None, profile).is_profile_running()
