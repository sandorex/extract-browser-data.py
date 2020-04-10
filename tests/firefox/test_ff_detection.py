# pylint: disable=unused-argument

import pytest

import extract_browser_data as ebd
import extract_browser_data.firefox.functions as func

from ..wrapper import FirefoxWrapper

pytestmark = pytest.mark.gui


def test_ff_running(xvfb, tmpdir, request):
   with FirefoxWrapper(tmpdir,
                       executable=request.config.getoption("--firefox")):
      assert func.read_profile_state(tmpdir) == func.ProfileState.RUNNING
      assert ebd.FirefoxProfile(None, tmpdir).is_profile_running()


def test_ff_not_running(xvfb, tmpdir, request):
   # start and stop firefox
   FirefoxWrapper(
       tmpdir, executable=request.config.getoption("--firefox")).start().stop()

   assert func.read_profile_state(tmpdir) == func.ProfileState.CLOSED
   assert not ebd.FirefoxProfile(None, tmpdir).is_profile_running()


def test_ff_crashed(xvfb, tmpdir, request):
   # start and kill firefox
   FirefoxWrapper(
       tmpdir, executable=request.config.getoption("--firefox")).start().kill()

   assert func.read_profile_state(tmpdir) == func.ProfileState.UNKNOWN

   # it should be detected as if it was running
   assert ebd.FirefoxProfile(None, tmpdir).is_profile_running()
