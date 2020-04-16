# pylint: disable=unused-argument

import extract_browser_data as ebd
import pytest

pytestmark = [pytest.mark.explicitly_run, pytest.mark.gui]


def test_ff_schema_containers(blank_profile):
   ebd.FirefoxProfile(None, blank_profile).reader().containers()


def test_ff_schema_last_session(blank_profile):
   ebd.FirefoxProfile(None, blank_profile).reader().last_session()


def test_ff_schema_account(blank_profile):
   ebd.FirefoxProfile(None, blank_profile).reader().account()


# CROSS BROWSER #
def test_ff_schema_extensions(blank_profile):
   ebd.FirefoxProfile(None, blank_profile).reader().extensions()


def test_ff_schema_history(blank_profile):
   ebd.FirefoxProfile(None, blank_profile).reader().history()


def test_ff_schema_bookmarks(blank_profile):
   ebd.FirefoxProfile(None, blank_profile).reader().bookmarks()


def test_ff_schema_cookies(blank_profile):
   ebd.FirefoxProfile(None, blank_profile).reader().cookies()
