"""Corba client."""
from __future__ import unicode_literals

import logging
import random
import string

from omniORB import CORBA

_LOGGER = logging.getLogger(__name__)


def sane_repr(obj, max_length):
    """Return object representation limited to `max_length` characters."""
    obj_repr = repr(obj)
    if len(obj_repr) > max_length:
        return obj_repr[:max_length] + ' [truncated]...'
    else:
        return obj_repr


ALLOWED_CHARS = string.ascii_letters + string.digits


class CorbaClient(object):
    """
    Corba client - wrapper over Corba object.

    @cvar max_length: Maximum length of `result` represantation in logs.
    """

    max_length = 2048

    def __init__(self, corba_object, recoder, server_error_cls=None):
        """
        Initialize instance.

        @param corba_object: Corba object to be wrapped.
        @type corba_object: `omniORB.CORBA.Object`
        @param recoder: Corba recoder used to encode/decode data.
        @type recoder: `CorbaRecoder`
        @param server_error_cls: INTERNAL_SERVER_ERROR class - exception defined in IDL handled as server error.
        @type server_error_cls: `type`
        """
        self.corba_object = corba_object
        self.recoder = recoder
        self.server_error_cls = server_error_cls

    # This method doesn't have **kwargs because Corba doesn't support it, at least not in the current version.
    def _call(self, method, *args):
        """Actually perform the Corba call."""
        # Generate identifier to mark matching logs
        call_id = ''.join(random.choice(ALLOWED_CHARS) for i in range(4))
        _LOGGER.debug("[%s] %s(%r)", call_id, method, args)

        # Encode strings
        args = self.recoder.encode(args)
        try:
            result = getattr(self.corba_object, method)(*args)
        except self.server_error_cls as error:
            _LOGGER.error("[%s] %s failed with %s", call_id, method, error)
            raise
        except CORBA.UserException as error:
            # All other exceptions defined in IDL
            _LOGGER.debug("[%s] %s failed with %s", call_id, method, error)
            raise
        except CORBA.Exception as error:
            # All other CORBA exceptions
            _LOGGER.error("[%s] %s failed with %s", call_id, method, error)
            raise

        # Log result before decoding
        _LOGGER.debug("[%s] %s returned %s", call_id, method, sane_repr(result, self.max_length))

        # Return decoded result
        return self.recoder.decode(result)

    def __getattr__(self, name):
        """Publish CORBA object methods."""
        def wrapper(*args):
            return self._call(name, *args)
        return wrapper


# Allows simple modification of client in tests, while keeping nice imports in code.
class CorbaClientProxy(object):
    """
    Proxy for Corba client instance.

    @ivar client: Corba client instance
    @type client: `CorbaClient`
    """

    def __init__(self, client):
        self.client = client

    def __getattr__(self, name):
        return getattr(self.client, name)
