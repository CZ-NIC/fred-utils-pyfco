# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(name='fred-pyfco',
      version='1.13.0',
      description='PYthon Fred COrba utilities',
      author='Vlastimil Zíma, CZ.NIC',
      author_email='vlastimil.zima@nic.cz',
      license='GNU GPL',
      platforms=['posix'],
      packages=find_packages(),
      install_requires=open('requirements.txt').read().splitlines(),
      extras_require={'testing': ['mock', 'testfixtures'],
                      'quality': ['isort', 'flake8', 'pydocstyle']})
