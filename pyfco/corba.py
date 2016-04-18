import sys

import CosNaming
import omniORB


# System Exception Handlers
# The call-back function must have the signature:
#
# function(cookie, retries, exc) -> boolean
#
# When a TRANSIENT exception occurs, the function is called, passing the cookie object,
# a count of how many times the operation has been retried, and the TRANSIENT exception
# object itself. If the function returns true, the operation is retried; if it returns false,
# the TRANSIENT exception is raised in the application.


def transient_failure(cookie, retries, exc):
    '''
    Manage TRANSIENT exceptions.

    TRANSIENT exceptions can occur in many circumstances. One circumstance is as follows:

    * The client invokes on an object reference.
    * The object replies with a LOCATION_FORWARD message.
    * The client caches the new location and retries to the new location.
    * Time passes...
    * The client tries to invoke on the object again, using the cached, forwarded location.
    * The attempt to contact the object fails.
    * The ORB runtime resets the location cache and throws a TRANSIENT exception with minor
      code TRANSIENT_FailedOnForwarded.
    '''
    if retries > 10:
        return False  # Skip first 10 exceptions.
    else:
        return True


def comm_failure(cookie, retries, exc):
    "Postpone CORBA.COMM_FAILURE exception."
    if retries > 20:
        return False  # Skip first 20 exceptions.
    else:
        return True


def system_failure(cookie, retries, exc):
    "Postpone CORBA.COMM_FAILURE exception."
    if retries > 5:
        return False  # Skip first 5 exceptions.
    else:
        return True


def init_omniorb_exception_handles(cookie):
    "Bound exception handles with omniORB API."
    omniORB.installTransientExceptionHandler(cookie, transient_failure)
    omniORB.installCommFailureExceptionHandler(cookie, comm_failure)
    omniORB.installSystemExceptionHandler(cookie, system_failure)


class CorbaNameServiceClient(object):
    '''
    Corba name service client connects to the corba server.

    @ivar host_port: Host and port to the Corba service. E.g. 'hostname:port'.
    @type host_port: C{str}
    @ivar context_name: Context name for CosNaming.NameComponent context.
    @type context_name: C{str}
    @ivar context: Corba NamingContext instance.
    @type context: C{CosNaming._objref_NamingContext instance}
    @ivar orb: Module ORB.
    @type orb: C{omniORB.CORBA.ORB instance}
    '''

    def __init__(self, orb, host_port='localhost', context_name='fred'):
        self.host_port = host_port
        self.context_name = context_name
        self.context = None
        self.orb = orb

    def connect(self):
        "Connect to the corba server."
        obj = self.orb.string_to_object('corbaname::' + self.host_port)
        self.context = obj._narrow(CosNaming.NamingContext)

    def get_object(self, name, idl_object):
        """
        Get object from the corba server. Corba objects are loaded by omniORB.importIDL.

        @param name: Name of NameComponent object. For example: "Logger"
        @type name: C{str}
        @param idl_object: Module object imported from IDL.
        @type idl_object: C{classobj instance}
        """
        if self.context is None:
            self.connect()
        cosname = [CosNaming.NameComponent(self.context_name, "context"),
                   CosNaming.NameComponent(name, "Object")]
        return self.context.resolve(cosname)._narrow(idl_object)
