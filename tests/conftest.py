import pytest


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

      if check_marker(item, 'running') or check_marker(
          item, 'not_running') or check_marker(item, 'crashed'):
         item.add_marker(pytest.mark.docker)

      if not config.getoption("--docker") and check_marker(item, 'docker'):
         item.add_marker(
             pytest.mark.skip(reason="test can only run in docker environment"))


@pytest.fixture
def profile(request):
   if request.config.getoption("--docker"):
      return request.config.getoption("--profile")

   return None
