from sys import platform as PLATFORM

WIN32 = bool(PLATFORM in ['win32', 'cygwin'])
LINUX = bool(PLATFORM == 'linux')
MACOS = bool(PLATFORM == 'darwin')

import extract_browser_data.api.util as util
import extract_browser_data.api.browsers
