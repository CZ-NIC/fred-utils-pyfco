from __future__ import unicode_literals

import warnings

from .recoder import CorbaRecoder, c2u, recoder, u2c

__all__ = ['CorbaRecoder', 'c2u', 'recoder', 'u2c']

warnings.warn("Model 'pyfco.corbarecoder' moved to 'pyfco.recoder'.", DeprecationWarning)
