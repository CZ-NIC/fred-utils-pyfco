#
# Copyright (C) 2015-2021  CZ.NIC, z. s. p. o.
#
# This file is part of FRED.
#
# FRED is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FRED is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FRED.  If not, see <https://www.gnu.org/licenses/>.
"""PYthon Fred COrba utilities."""
from __future__ import unicode_literals

from .client import CorbaClient, CorbaClientProxy
from .name_service import CorbaNameServiceClient
from .recoder import CorbaRecoder, c2u, u2c

__version__ = '1.16.2'
__all__ = ['CorbaClient', 'CorbaClientProxy', 'CorbaNameServiceClient', 'CorbaRecoder', 'c2u', 'u2c']
