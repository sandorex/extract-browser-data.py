# pylint: disable=unused-argument

import extract_browser_data as ebd
import pytest

pytestmark = [pytest.mark.explicitly_run, pytest.mark.gui]


# CROSS BROWSER #
def test_ch_schema_extensions(blank_profile):
   ebd.ChromiumProfile(None, blank_profile[0]).reader().extensions()


def test_ch_schema_history(blank_profile):
   ebd.ChromiumProfile(None, blank_profile[0]).reader().history()


def test_ch_schema_bookmarks(blank_profile):
   ebd.ChromiumProfile(None, blank_profile[0]).reader().bookmarks()


def test_ch_schema_cookies(blank_profile):
   ebd.ChromiumProfile(None, blank_profile[0]).reader().cookies()
