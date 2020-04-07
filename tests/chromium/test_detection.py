import pytest
import extract_browser_data as ebd
import extract_browser_data.chromium.functions as func

pytestmark = pytest.mark.docker


def test_ch_running(profile):
   assert func.read_profile_state(profile) == func.ProfileState.RUNNING

   assert ebd.ChromiumProfile(None, profile).is_profile_running()


def test_ch_not_running(profile):
   assert func.read_profile_state(profile) == func.ProfileState.CLOSED

   assert not ebd.ChromiumProfile(None, profile).is_profile_running()


def test_ch_crashed(profile):
   assert func.read_profile_state(profile) == func.ProfileState.UNKNOWN

   # it should be detect as if it was running
   assert ebd.ChromiumProfile(None, profile).is_profile_running()
