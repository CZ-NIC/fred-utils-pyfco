# -*- coding: utf-8 -*-
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

from setuptools import find_packages, setup

setup(name='fred-pyfco',
      version='1.16.2',
      description='PYthon Fred COrba utilities',
      author='Vlastimil Zíma, CZ.NIC',
      author_email='vlastimil.zima@nic.cz',
      license='GPLv3+',
      platforms=['posix'],
      packages=find_packages(),
      install_requires=open('requirements.txt').read().splitlines(),
      extras_require={'test': ['mock', 'testfixtures'],
                      'quality': ['isort', 'flake8', 'pydocstyle']})
