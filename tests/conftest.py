import os
import sys
import pytest

from distutils import dir_util


def check_marker(item, marker):
   return next(item.iter_markers(name=marker), None) is not None


def pytest_addoption(parser):
   parser.addoption(
       "--profile",
       default=None,
       type=str,
       help=
       "provide a path to profile to use during testing (only with --docker)")
   parser.addoption("--docker",
                    action="store_true",
                    default=False,
                    help="run tests that require automation.")


def pytest_collection_modifyitems(config, items):
   for item in items:
      if item.name.startswith('test_ff_'):
         item.add_marker(pytest.mark.firefox)
         item.add_marker(pytest.mark.browser)
      elif item.name.startswith('test_ch_'):
         item.add_marker(pytest.mark.chromium)
         item.add_marker(pytest.mark.browser)

      if item.name.endswith('_win32'):
         item.add_marker(pytest.mark.win32)
      elif item.name.endswith('_linux'):
         item.add_marker(pytest.mark.linux)
      elif item.name.endswith('_macos'):
         item.add_marker(pytest.mark.macos)
      elif item.name.endswith('_unix'):
         item.add_marker(pytest.mark.unix)
      else:
         item.add_marker(pytest.mark.win32)
         item.add_marker(pytest.mark.linux)
         item.add_marker(pytest.mark.macos)

      if check_marker(item, 'running') or check_marker(
          item, 'not_running') or check_marker(item, 'crashed'):
         item.add_marker(pytest.mark.docker)

      if not config.getoption("--docker") and check_marker(item, 'docker'):
         item.add_marker(
             pytest.mark.skip(reason="test can only run in docker environment"))

      if sys.platform == 'win32' and not check_marker(item, 'win32'):
         item.add_marker(
             pytest.mark.skip(reason="test can only run on windows"))
      elif sys.platform == 'linux' and not (check_marker(item, 'linux')
                                            or check_marker(item, 'unix')):
         item.add_marker(pytest.mark.skip(reason="test can only run on linux"))
      elif sys.platform == 'darwin' and not (check_marker(item, 'macos')
                                             or check_marker(item, 'unix')):
         item.add_marker(pytest.mark.skip(reason="test can only run on macos"))


@pytest.fixture
def profile(request):
   if request.config.getoption("--docker"):
      return request.config.getoption("--profile")

   return None


@pytest.fixture
def datadir(tmpdir, request):
   '''
   Fixture responsible for searching a folder with the same name of test
   module and, if available, moving all contents to a temporary directory so
   tests can use them freely.
   '''
   # https://stackoverflow.com/a/29631801/6251201
   filename = request.module.__file__
   test_dir = os.path.splitext(filename)

   if os.path.isdir(test_dir):
      dir_util.copy_tree(test_dir, str(tmpdir))

   return tmpdir
