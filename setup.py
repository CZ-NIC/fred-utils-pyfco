# Setup MUST be from freddist.
# It does not work with fred-manager if it is from distutils.core.
from freddist.core import setup

setup(name='pyfco',
      version='1.0.0',
      description='Python Fred Corba utilities',
      packages=('pyfco', ),
      )
