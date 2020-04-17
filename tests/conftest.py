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


def has_markers(item, *markers):
   return all(
       next(item.iter_markers(name=marker), None) is not None
       for marker in markers)


def pytest_addoption(parser):
   parser.addoption('--chromium',
                    default='chromium-browser',
                    type=str,
                    help="chromium executable (default 'chromium-browser')")

   parser.addoption('--firefox',
                    default='firefox',
                    type=str,
                    help="firefox executable (default 'firefox')")

   if LINUX:
      parser.addoption('--no-xvfb',
                       action='store_false',
                       default=True,
                       help='do not use xvfb for gui tests (linux only)')


def pytest_configure(config):
   pytest.FIREFOX_VERSION = FirefoxWrapper.read_version(
       config.getoption('--firefox'))
   pytest.CHROMIUM_VERSION = ChromiumWrapper.read_version(
       config.getoption('--chromium'))


def pytest_sessionstart(session):
   if pytest.FIREFOX_VERSION is not None:
      print(f'Found Firefox version {pytest.FIREFOX_VERSION[0]}')
   else:
      print('Firefox not found')

   if pytest.CHROMIUM_VERSION is not None:
      print(f'Found Chromium version {pytest.CHROMIUM_VERSION[0]}')
   else:
      print('Chromium not found')


def pytest_collection_modifyitems(items, config):
   for item in items:
      if item.name.startswith('test_ch_'):
         item.add_marker(pytest.mark.chromium)
         item.add_marker(pytest.mark.browser)
      elif item.name.startswith('test_ff_'):
         item.add_marker(pytest.mark.firefox)
         item.add_marker(pytest.mark.browser)

      if has_markers(item, 'gui'):
         if has_markers(item, 'firefox') and pytest.FIREFOX_VERSION is None:
            item.add_marker(
                pytest.mark.skip(reason='the test requires Firefox executable'))
         elif has_markers(item, 'chromium') and pytest.CHROMIUM_VERSION is None:
            item.add_marker(
                pytest.mark.skip(
                    reason='the test requires Chromium executable'))

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

      if WIN32 and not has_markers(item, 'win32'):
         item.add_marker(
             pytest.mark.skip(reason='the test does not run on windows'))
      elif LINUX and not (has_markers(item, 'linux')
                          or has_markers(item, 'unix')):
         item.add_marker(
             pytest.mark.skip(reason='the test does not run on linux'))
      elif MACOS and not (has_markers(item, 'macos')
                          or has_markers(item, 'unix')):
         item.add_marker(
             pytest.mark.skip(reason='the test does not run on macos'))

      # tests that can run only explicitly
      if has_markers(item, 'explicitly_run') and not has_markers(item, 'skip'):
         for arg in config.args:
            if arg == item.nodeid or Path(item.fspath).samefile(arg):
               break
         else:
            item.add_marker(
                pytest.mark.skip(
                    reason='the test can only run when explicitly selected'))


@pytest.fixture(scope='session')
def xvfb(request):
   """Sets up xvfb and fluxbox

   This fixture does nothing on platforms other than linux, to disable on linux
   use --no-xvfb flag
   """
   # skip running xvfb but still run the test
   if not LINUX or not request.config.getoption('--no-xvfb'):
      yield
      return

   DISPLAY = ':99'

   if os.path.exists('/tmp/.X11-unix/X' + DISPLAY[1:]):
      pytest.fail(f'x server is already running at display {DISPLAY}')

   xvfb_process = subprocess.Popen(
       ['Xvfb', DISPLAY, '-screen', '0', '1280x1024x24'])

   if xvfb_process.poll():
      pytest.fail('xvfb has quit unexpectedly')

   # set the environment variable
   os.environ['DISPLAY'] = DISPLAY

   print('starting xvfb')

   # wait for xvfb
   counter = 0
   while subprocess.call(
       ['xdpyinfo'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
      time.sleep(1)
      counter += 1

      if counter > 20:
         xvfb_process.send_signal(signal.SIGQUIT)
         xvfb_process.wait(10)
         pytest.fail('timeout for xvfb has been exceeded, aborting..')

   wm_process = subprocess.Popen(['fluxbox'],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)

   if wm_process.poll():
      pytest.fail('the window manager has quit unexpectedly')

   print('starting the window manager')

   # wait for the wm
   counter = 0
   while subprocess.call(['wmctrl', '-m'],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL) != 0:
      time.sleep(1)
      counter += 1

      if counter > 20:
         wm_process.send_signal(signal.SIGQUIT)
         wm_process.wait(10)
         pytest.fail('timeout for window manager has been exceeded, aborting..')

   # run tests
   yield

   # tell them to terminate
   print('quitting fluxbox')
   wm_process.send_signal(signal.SIGQUIT)
   wm_process.wait(10)

   print('quitting xvfb')
   xvfb_process.send_signal(signal.SIGQUIT)
   xvfb_process.wait(10)


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
