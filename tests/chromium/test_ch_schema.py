# pylint: disable=unused-argument

import pytest

import extract_browser_data as ebd

pytestmark = [pytest.mark.explicitly_run, pytest.mark.gui]


# CROSS BROWSER #
def test_ch_schema_extensions(new_chromium_profile):
   ebd.ChromiumProfile(None, new_chromium_profile[0]).reader().extensions()


def test_ch_schema_history(new_chromium_profile):
   ebd.ChromiumProfile(None, new_chromium_profile[0]).reader().history()


def test_ch_schema_bookmarks(new_chromium_profile):
   ebd.ChromiumProfile(None, new_chromium_profile[0]).reader().bookmarks()


def test_ch_schema_cookies(new_chromium_profile):
   ebd.ChromiumProfile(None, new_chromium_profile[0]).reader().cookies()
