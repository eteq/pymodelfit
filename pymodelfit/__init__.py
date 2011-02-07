#Copyright 2009 Erik Tollerud
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
pymodelfit -- a pythonic, object-oriented framework and GUI tool for fitting
data to models.
"""

_release = True
_majorversion = 0
_minorversion = 1
_bugfix = 1
version = str(_majorversion) + '.' + str(_minorversion) + \
          ('' if _bugfix is None else ('.'+str(_bugfix))) + \
          ('' if _release else 'dev')

from core import *
from builtins import * #do this to register all the builtins
