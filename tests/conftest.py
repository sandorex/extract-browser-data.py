# pylint: disable=unused-argument,redefined-outer-name

import os
import signal
import subprocess
import sys
import time
from distutils import dir_util
from pathlib import Path

import pytest

from .wrapper import ChromiumWrapper, FirefoxWrapper

DIR = Path(__file__).parent

WIN32 = False
LINUX = False
MACOS = False
UNIX = False

if sys.platform == 'win32':
   WIN32 = True
elif sys.platform == 'linux':
   LINUX = True
   UNIX = True
elif sys.platform == 'darwin':
   MACOS = True
   UNIX = True


def check_marker(item, marker):
   return next(item.iter_markers(name=marker), None) is not None


def pytest_addoption(parser):
   parser.addoption("--firefox",
                    default='firefox',
                    type=str,
                    help="firefox executable (default 'firefox')")
   parser.addoption("--chromium",
                    default='chromium-browser',
                    type=str,
                    help="chromium executable (default 'chromium-browser')")

   parser.addoption("--docker",
                    action="store_true",
                    default=False,
                    help="run docker only tests")

   if LINUX:
      parser.addoption("--no-xvfb",
                       action="store_false",
                       default=True,
                       help="do not use xvfb for gui tests (linux only)")


def pytest_collection_modifyitems(items, config):
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
         item.add_marker(pytest.mark.unix)
      elif item.name.endswith('_macos'):
         item.add_marker(pytest.mark.macos)
         item.add_marker(pytest.mark.unix)
      elif item.name.endswith('_unix'):
         item.add_marker(pytest.mark.unix)
      else:
         item.add_marker(pytest.mark.win32)
         item.add_marker(pytest.mark.linux)
         item.add_marker(pytest.mark.macos)
         item.add_marker(pytest.mark.unix)

      if WIN32 and not check_marker(item, 'win32'):
         item.add_marker(pytest.mark.skip())
      elif LINUX and not (check_marker(item, 'linux')
                          or check_marker(item, 'unix')):
         item.add_marker(pytest.mark.skip())
      elif MACOS and not (check_marker(item, 'macos')
                          or check_marker(item, 'unix')):
         item.add_marker(pytest.mark.skip())

      if check_marker(item, 'docker') and not config.getoption("--docker"):
         item.add_marker(pytest.mark.skip())


@pytest.fixture(scope='session')
def xvfb(request):
   """Sets up xvfb and fluxbox

   This fixture does nothing on platforms other than linux, to disable on linux
   use --no-xvfb flag
   """
   if not LINUX or not request.config.getoption("--no-xvfb"):
      yield
      return

   DISPLAY = ':99'

   if os.path.exists('/tmp/.X11-unix/X' + DISPLAY[1:]):
      raise Exception(f'x server is already running at display {DISPLAY}')

   xvfb_process = subprocess.Popen(
       ['Xvfb', DISPLAY, '-screen', '0', '1280x1024x24'])

   if xvfb_process.poll():
      raise Exception('xvfb has quit unexpectedly')

   # set the environment variable
   os.environ['DISPLAY'] = DISPLAY

   # wait for xvfb
   counter = 0
   while not subprocess.call(
       ['xdpyinfo'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
      time.sleep(1)
      counter += 1

      if counter > 20:
         xvfb_process.send_signal(signal.SIGQUIT)
         raise Exception('timeout for xvfb has been exceeded, aborting..')

   fluxbox_process = subprocess.Popen(['fluxbox'],
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL)

   if fluxbox_process.poll():
      raise Exception('fluxbox has quit unexpectedly')

   # wait for fluxbox
   counter = 0
   while not subprocess.call(
       ['wmctrl', '-m'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
      time.sleep(1)
      counter += 1

      if counter > 20:
         fluxbox_process.send_signal(signal.SIGQUIT)
         raise Exception('timeout for fluxbox has been exceeded, aborting..')

   # run tests
   yield

   # tell them to terminate
   fluxbox_process.send_signal(signal.SIGQUIT)
   fluxbox_process.wait()

   xvfb_process.send_signal(signal.SIGQUIT)
   xvfb_process.wait()


@pytest.fixture
def firefox_profile(tmpdir):
   dir_util.copy_tree(os.path.join(DIR, 'firefox', 'profile'), str(tmpdir))

   return tmpdir


@pytest.fixture
def chromium_profile(tmpdir):
   dir_util.copy_tree(os.path.join(DIR, 'chromium', 'user_data_dir'),
                      str(tmpdir))

   return tmpdir / 'Default', tmpdir


@pytest.fixture
def new_firefox_profile(tmpdir, xvfb):
   FirefoxWrapper(tmpdir).start().stop()

   return tmpdir


@pytest.fixture
def new_chromium_profile(tmpdir, xvfb):
   ChromiumWrapper(tmpdir).start().stop()

   return tmpdir / 'Default', tmpdir


@pytest.fixture
def datadir(tmpdir, request):
   '''Fixture responsible for searching a folder with the same name of test
   module and, if available, moving all contents to a temporary directory so
   tests can use them freely.
   '''
   # https://stackoverflow.com/a/29631801/6251201
   filename = request.module.__file__
   test_dir, _ = os.path.splitext(filename)

   if os.path.isdir(test_dir):
      dir_util.copy_tree(test_dir, str(tmpdir))

   return tmpdir
