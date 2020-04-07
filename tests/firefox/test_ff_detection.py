import pytest
import extract_browser_data as ebd
import extract_browser_data.firefox.functions as func

pytestmark = pytest.mark.docker


def test_ff_running(profile):
   assert func.read_profile_state(profile) == func.ProfileState.RUNNING

   assert ebd.FirefoxProfile(None, profile).is_profile_running()


def test_ff_not_running(profile):
   assert func.read_profile_state(profile) == func.ProfileState.CLOSED

   assert not ebd.FirefoxProfile(None, profile).is_profile_running()


def test_ff_crashed(profile):
   assert func.read_profile_state(profile) == func.ProfileState.UNKNOWN

   # it should be detect as if it was running
   assert ebd.FirefoxProfile(None, profile).is_profile_running()
