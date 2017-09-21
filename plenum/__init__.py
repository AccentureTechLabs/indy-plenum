"""
plenum package

"""
from __future__ import absolute_import, division, print_function

import sys
if sys.version_info < (3, 5, 0):
    raise ImportError("Python 3.5.0 or later required.")

import os   # noqa
from importlib.util import module_from_spec, spec_from_file_location    # noqa: E402

import plenum   # noqa: E402
import plenum.server.plugin     # noqa: E402
from plenum.config import ENABLED_PLUGINS   # noqa: E402


PLUGIN_LEDGER_IDS = set()


def setup_plugins():
    global PLUGIN_LEDGER_IDS
    for plugin_name in ENABLED_PLUGINS:
        plugin_path = os.path.join(plenum.server.plugin.__path__[0],
                                   plugin_name, '__init__.py')
        spec = spec_from_file_location('__init__.py', plugin_path)
        init = module_from_spec(spec)
        spec.loader.exec_module(init)
        if 'LEDGER_IDS' in init.__dict__:
            PLUGIN_LEDGER_IDS.update(init.__dict__['LEDGER_IDS'])


setup_plugins()


from .__metadata__ import *  # noqa

from plenum.common.jsonpickle_util import setUpJsonpickle   # noqa: E402
setUpJsonpickle()
