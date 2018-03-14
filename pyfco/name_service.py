from __future__ import unicode_literals

import logging
import warnings

import CosNaming
import six
from omniORB import CORBA, installTransientExceptionHandler

_LOGGER = logging.getLogger(__name__)


def init_omniorb_exception_handles(cookie):
    """Bound exception handles with omniORB API."""
    warnings.warn("'init_omniorb_exception_handles' is obsolete and does nothing. It should be removed.",
                  DeprecationWarning)


class CorbaNameServiceClient(object):
    """
    Corba name service client connects to the corba server.

    @ivar host_port: Host and port to the Corba service. E.g. 'hostname:port'.
    @type host_port: C{six.text_type}
    @ivar context_name: Context name for CosNaming.NameComponent context.
    @type context_name: C{six.text_type}
    @ivar context: Corba NamingContext instance.
    @type context: C{CosNaming._objref_NamingContext instance}
    @ivar retries: Maximal number of retries on error.
    @type retries: int

    @cvar orb_args: Arguments for CORBA initialization.
    @type orb_args: [six.text_type, six.text_type, ...]
    """

    orb_args = ['-ORBnativeCharCodeSet', 'UTF-8']

    def __init__(self, orb=None, host_port='localhost', context_name='fred', retries=5):
        if orb is not None:
            warnings.warn("'orb' argument is deprecated and should be removed.", DeprecationWarning)
        if isinstance(host_port, six.binary_type):
            warnings.warn("Passing 'host_port' as six.binary_type is deprecated. Please pass six.text_type.",
                          DeprecationWarning)
            self.host_port = host_port.decode()
        else:
            self.host_port = host_port
        if isinstance(context_name, six.binary_type):
            warnings.warn("Passing 'context_name' as six.binary_type is deprecated. Please pass six.text_type.",
                          DeprecationWarning)
            self.context_name = context_name.decode()
        else:
            self.context_name = context_name
        self.context = None
        self.retries = retries

    def retry_handler(self, cookie, retries, exc):
        """Handle corba error and retry, unless number of retries is too high."""
        _LOGGER.debug("Handling corba error %r - %r retries.", exc, retries)
        if retries >= self.retries:
            return False
        else:
            return True

    def connect(self):
        """Connect to the corba server and attach TRANSIENT error handler."""
        orb_args = []
        for orb_arg in self.orb_args:
            if isinstance(orb_arg, six.text_type):
                orb_arg = orb_arg.encode()
            orb_args.append(orb_arg)
        orb = CORBA.ORB_init(orb_args)
        obj = orb.string_to_object('corbaname::' + self.host_port)
        installTransientExceptionHandler(None, self.retry_handler, obj)
        self.context = obj._narrow(CosNaming.NamingContext)

    def get_object(self, name, idl_object):
        """
        Get object from the corba server. Corba objects are loaded by omniORB.importIDL.

        @param name: Name of NameComponent object. For example: "Logger"
        @type name: C{six.text_type}
        @param idl_object: Module object imported from IDL.
        @type idl_object: C{classobj instance}
        """
        if self.context is None:
            self.connect()
        if isinstance(name, six.text_type):
            name = name.encode()
        else:
            warnings.warn("Passing 'name' as six.binary_type is deprecated. Please pass six.text_type.",
                          DeprecationWarning)
        context_name = self.context_name.encode()
        cosname = [CosNaming.NameComponent(context_name, b"context"),
                   CosNaming.NameComponent(name, b"Object")]
        return self.context.resolve(cosname)._narrow(idl_object)
