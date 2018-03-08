# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(name='fred-pyfco',
      version='1.10.0',
      description='PYthon Fred COrba utilities',
      author='Vlastimil Zíma, CZ.NIC',
      author_email='vlastimil.zima@nic.cz',
      license='GNU GPL',
      platforms=['posix'],
      packages=find_packages(),
      install_requires=['pytz'])
