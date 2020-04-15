# pylint: disable=unused-argument

import pytest

import extract_browser_data as ebd

pytestmark = [pytest.mark.explicitly_run, pytest.mark.gui]


def test_ff_schema_containers(new_firefox_profile):
   ebd.FirefoxProfile(None, new_firefox_profile).reader().containers()


def test_ff_schema_last_session(new_firefox_profile):
   ebd.FirefoxProfile(None, new_firefox_profile).reader().last_session()


def test_ff_schema_account(new_firefox_profile):
   ebd.FirefoxProfile(None, new_firefox_profile).reader().account()


# CROSS BROWSER #
def test_ff_schema_extensions(new_firefox_profile):
   ebd.FirefoxProfile(None, new_firefox_profile).reader().extensions()


def test_ff_schema_history(new_firefox_profile):
   ebd.FirefoxProfile(None, new_firefox_profile).reader().history()


def test_ff_schema_bookmarks(new_firefox_profile):
   ebd.FirefoxProfile(None, new_firefox_profile).reader().bookmarks()


def test_ff_schema_cookies(new_firefox_profile):
   ebd.FirefoxProfile(None, new_firefox_profile).reader().cookies()
