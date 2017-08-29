"""
plenum package

"""
from __future__ import absolute_import, division, print_function

import sys
if sys.version_info < (3, 5, 0):
    raise ImportError("Python 3.5.0 or later required.")

import plenum   # noqa: E402
import plenum.server.plugin     # noqa: E402

from .__metadata__ import *  # noqa

from plenum.common.jsonpickle_util import setUpJsonpickle   # noqa: E402
setUpJsonpickle()
