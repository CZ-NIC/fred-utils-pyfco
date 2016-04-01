import codecs
import copy
import types

from omniORB import EnumItem, StructBase


class UnsupportedEncodingError(Exception):
    pass


class CorbaRecoder(object):
    """ Encodes and decodes corba entities to python entities, i.e.,
        essentially converts corba strings to python strings (type depends on
        specified encoding).
    """

    def __init__(self, coding='ascii'):
        try:
            codecs.lookup(coding)
            self.coding = coding
        except LookupError, e:
            raise UnsupportedEncodingError(e)

        self.encode_functions = {}
        self.decode_functions = {}
        self.add_recode_function(str, self._decode_str, self._identity)
        self.add_recode_function(unicode, self._identity, self._encode_unicode)
        self.add_recode_function(bool, self._identity, self._identity)
        self.add_recode_function(float, self._identity, self._identity)
        self.add_recode_function(int, self._identity, self._identity)
        self.add_recode_function(long, self._identity, self._identity)
        self.add_recode_function(types.NoneType, self._identity, self._identity)
        self.add_recode_function(types.TupleType, self._decode_iter, self._encode_iter)
        self.add_recode_function(types.ListType, self._decode_iter, self._encode_iter)
        self.add_recode_function(StructBase, self._decode_struct, self._encode_struct)
        # Do not decode/encode enum items
        self.add_recode_function(EnumItem, self._identity, self._identity)

    def add_recode_function(self, typeobj, decode_function, encode_function):
        self.decode_functions[typeobj] = decode_function
        self.encode_functions[typeobj] = encode_function

    def _identity(self, val):
        return val

    def _decode_str(self, val):
        """ Decodes str to unicode
        """
        return val.decode(self.coding)

    def _encode_unicode(self, val):
        """ Encodes unicode to str
        """
        return val.encode(self.coding)

    def _decode_iter(self, val):
        """ Iter over iterable and recursively decodes
        """
        return type(val)([self.decode(x) for x in val])

    def _encode_iter(self, val):
        """ Iter over iterable and recursively encodes
        """
        return type(val)([self.encode(x) for x in val])

    def _decode_struct(self, val):
        """
        Returns decoded Corba structure.

        Decodes all attributes.
        """
        answer = copy.copy(val)
        for name in dir(answer):
            item = getattr(answer, name)
            if name.startswith('_'):
                continue
            else:
                answer.__dict__[name] = self.decode(item)
        return answer

    def _encode_struct(self, val):
        """
        Returns encoded Corba structure.

        Encodes all attributes.
        """
        answer = copy.copy(val)
        for name in dir(answer):
            item = getattr(answer, name)
            if name.startswith('_'):
                continue
            else:
                answer.__dict__[name] = self.encode(item)
        return answer

    def _decode_other(self, val):
        """ Raise error on other types
            Can be overridden to decode it
        """
        raise ValueError("%s can not be decoded." % val)

    def _encode_other(self, val):
        """ Raise error on other types
            Can be overridden to encode it
        """
        raise ValueError("%s can not be encoded." % val)

    def _get_parents(self, val):
        """Returns all parents of the instance."""
        return (val.__class__, ) + val.__class__.__bases__

    def decode(self, answer):
        """Returns answer decoded from Corba to Python."""
        for cls in self._get_parents(answer):
            if cls in self.decode_functions:
                return self.decode_functions[cls](answer)
        else:
            return self._decode_other(answer)  # other unsupported type

    def encode(self, answer):
        """Returns answer encoded from Python to Corba."""
        for cls in self._get_parents(answer):
            if cls in self.encode_functions:
                return self.encode_functions[cls](answer)
        else:
            return self._encode_other(answer)  # other unsupported type


recoder = CorbaRecoder('utf-8')
c2u = recoder.decode  # recode from corba string to unicode
u2c = recoder.encode  # recode from unicode to strings
