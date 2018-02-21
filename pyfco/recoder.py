from __future__ import unicode_literals

import codecs
import copy
import re
import types
from datetime import datetime

import pytz
from omniORB import EnumItem, StructBase

try:
    from fred_idl.Registry import IsoDate, IsoDateTime
except ImportError:
    IsoDate = None
    IsoDateTime = None


ISO_DATETIME_PATTERN = re.compile('^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})T'
                                  '(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(.(?P<microsecond>\d{6}))?'
                                  '(?P<tzinfo>Z|[+-]\d{2}:?\d{2})$')


def decode_iso_date(value):
    """Decode IsoDate struct to date object.

    @raise ValueError: If date can't be parsed.
    """
    return datetime.strptime(value.value, '%Y-%m-%d').date()


def encode_iso_date(value):
    """Encode date object into IsoDate struct."""
    if IsoDate is None:
        raise RuntimeError("fred_idl.Registry.IsoDate struct is not found.")
    return IsoDate(value.isoformat())


def decode_iso_datetime(value):
    """Decode IsoDateTime struct to aware datetime object.

    @raise ValueError: If date time can't be parsed.
    """
    match = ISO_DATETIME_PATTERN.match(value.value)
    if match is None:
        raise ValueError("{} datetime can't be decoded.".format(value))
    kwargs = {k: int(v) for k, v in match.groupdict().items() if k != 'tzinfo' and v is not None}
    tzinfo = match.group('tzinfo')
    if tzinfo == 'Z':
        kwargs['tzinfo'] = pytz.utc
    else:
        hours = int(tzinfo[1:3])
        minutes = int(tzinfo[3:].strip(':'))
        offset = minutes + 60 * hours
        sign = tzinfo[0]
        if sign == '-':
            offset = -offset
        kwargs['tzinfo'] = pytz.FixedOffset(offset)
    return datetime(**kwargs)


def encode_iso_datetime(value):
    """Encode datetime object into IsoDateTime struct."""
    if IsoDateTime is None:
        raise RuntimeError("fred_idl.Registry.IsoDateTime struct is not found.")
    return IsoDateTime(value.isoformat())


class UnsupportedEncodingError(Exception):
    pass


class CorbaRecoder(object):
    """Encode and decode corba entities to python entities.

    Essentially converts corba strings to python strings (type depends on specified encoding).
    """

    def __init__(self, coding='ascii'):
        try:
            codecs.lookup(coding)
            self.coding = coding
        except LookupError as e:
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
        """Decode str to unicode."""
        return val.decode(self.coding)

    def _encode_unicode(self, val):
        """Encode unicode to str."""
        return val.encode(self.coding)

    def _decode_iter(self, val):
        """Iterate over iterable and recursively decode."""
        return type(val)([self.decode(x) for x in val])

    def _encode_iter(self, val):
        """Iterate over iterable and recursively encode."""
        return type(val)([self.encode(x) for x in val])

    def _decode_struct(self, val):
        """
        Return decoded Corba structure.

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
        Return encoded Corba structure.

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
        """Raise error on other types. Can be overridden to decode it."""
        raise ValueError("%s can not be decoded." % val)

    def _encode_other(self, val):
        """Raise error on other types. Can be overridden to encode it."""
        raise ValueError("%s can not be encoded." % val)

    def _get_parents(self, val):
        """Return all parents of the instance."""
        return (val.__class__, ) + val.__class__.__bases__

    def decode(self, answer):
        """Return answer decoded from Corba to Python."""
        for cls in self._get_parents(answer):
            if cls in self.decode_functions:
                return self.decode_functions[cls](answer)
        else:
            return self._decode_other(answer)  # other unsupported type

    def encode(self, answer):
        """Return answer encoded from Python to Corba."""
        for cls in self._get_parents(answer):
            if cls in self.encode_functions:
                return self.encode_functions[cls](answer)
        else:
            return self._encode_other(answer)  # other unsupported type


recoder = CorbaRecoder('utf-8')
c2u = recoder.decode  # recode from corba string to unicode
u2c = recoder.encode  # recode from unicode to strings
