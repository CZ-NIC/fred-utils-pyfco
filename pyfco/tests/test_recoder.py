#
# Copyright (C) 2015-2020  CZ.NIC, z. s. p. o.
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
from __future__ import unicode_literals

import copy
import unittest
from datetime import date, datetime

import pytz
import six
from fred_idl.Registry import IsoDate, IsoDateTime
from omniORB import EnumItem, StructBase

from pyfco.recoder import CorbaRecoder, UnsupportedEncodingError, decode_iso_date, decode_iso_datetime, \
    encode_iso_date, encode_iso_datetime
from pyfco.utils import CorbaAssertMixin

TEST_ENUM_ITEM = EnumItem("MyEnumItem", 42)


class TestIsoDate(CorbaAssertMixin, unittest.TestCase):
    """Test `decode_iso_date` and `encode_iso_date` functions."""

    def test_decode(self):
        self.assertEqual(decode_iso_date(IsoDate('1970-02-01')), date(1970, 2, 1))

    def test_encode(self):
        self.assertEqual(encode_iso_date(date(1970, 2, 1)), IsoDate('1970-02-01'))


class TestIsoDateTime(CorbaAssertMixin, unittest.TestCase):
    """Test `decode_iso_datetime` and `encode_iso_datetime` functions."""

    def test_decode(self):
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16Z')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.utc))

    def test_decode_zones(self):
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16+0000')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.utc))
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16+00:00')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.utc))
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16-0000')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.utc))
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16-00:00')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.utc))

        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16+0005')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.FixedOffset(5)))
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16+0020')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.FixedOffset(20)))
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16+0100')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.FixedOffset(60)))

        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16+1000')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.FixedOffset(600)))
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16+10:00')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.FixedOffset(600)))
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16-1000')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.FixedOffset(-600)))
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16-10:00')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.FixedOffset(-600)))

        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16+1135')),
                         datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.FixedOffset(695)))

    def test_decode_microseconds(self):
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16.123456Z')),
                         datetime(1970, 2, 1, 12, 14, 16, 123456, tzinfo=pytz.utc))
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16.000123Z')),
                         datetime(1970, 2, 1, 12, 14, 16, 123, tzinfo=pytz.utc))
        self.assertEqual(decode_iso_datetime(IsoDate('1970-02-01T12:14:16.000123+0200')),
                         datetime(1970, 2, 1, 12, 14, 16, 123, tzinfo=pytz.FixedOffset(120)))

    def test_decode_invalid(self):
        self.assertRaises(ValueError, decode_iso_datetime, IsoDateTime('1970-02-31T04:06:08Z'))
        self.assertRaises(ValueError, decode_iso_datetime, IsoDateTime('1970-02-03T04:06:08.666Z'))
        # Datetime without a zone
        self.assertRaises(ValueError, decode_iso_datetime, IsoDateTime('1970-02-03T04:06:08'))

    def test_encode(self):
        self.assertEqual(encode_iso_datetime(datetime(1970, 2, 1, 12, 14, 16, tzinfo=pytz.utc)),
                         IsoDateTime('1970-02-01T12:14:16+00:00'))
        self.assertEqual(encode_iso_datetime(datetime(1970, 2, 1, 12, 14, 16, 123456, tzinfo=pytz.utc)),
                         IsoDateTime('1970-02-01T12:14:16.123456+00:00'))
        self.assertEqual(encode_iso_datetime(datetime(1970, 2, 1, 12, 14, 16, 123456, tzinfo=pytz.FixedOffset(90))),
                         IsoDateTime('1970-02-01T12:14:16.123456+01:30'))

    def test_encode_naive(self):
        self.assertRaises(ValueError, encode_iso_datetime, datetime(1970, 2, 1, 12, 14, 16))


class SampleCorbaStruct(StructBase):
    _NP_RepositoryId = "IDL:SampleCorbaStruct:1.0"

    def __init__(self, id, ico, dic, varSymb, vat, handle, name,
                 organization, street1, street2, street3, city,
                 stateorprovince, postalcode, country, telephone,
                 fax, email, url, credit, unspec_credit, access, zones, hidden):
        self.id = id
        self.ico = ico
        self.dic = dic
        self.varSymb = varSymb
        self.vat = vat
        self.handle = handle
        self.name = name
        self.organization = organization
        self.street1 = street1
        self.street2 = street2
        self.street3 = street3
        self.city = city
        self.stateorprovince = stateorprovince
        self.postalcode = postalcode
        self.country = country
        self.telephone = telephone
        self.fax = fax
        self.email = email
        self.url = url
        self.credit = credit
        self.unspec_credit = unspec_credit
        self.access = access
        self.zones = zones
        self.hidden = hidden


class NodeStruct(StructBase):
    """
    Simple corba structure for testing nested structures.
    """

    def __init__(self, text, inner):
        self.text = text
        self.inner = inner


class TestCorbaRecoder(unittest.TestCase):

    recoder_class = CorbaRecoder

    def test_create(self):
        """ CorbaRecoder is created with supported encoding. """
        rec = self.recoder_class("utf-8")
        self.assertIsNotNone(rec)

    def test_create_wrong_encoding(self):
        """ CorbaRecoder raises error for unsupported encoding. """
        self.assertRaises(UnsupportedEncodingError, self.recoder_class, "invalid coding")

    def test_decode_basic_types(self):
        """ CorbaRecoder decodes basic types to python correctly . """
        rec = self.recoder_class("utf-8")

        decoded_none = rec.decode(None)
        expected_none = None

        decoded_int = rec.decode(6)
        expected_int = 6

        decoded_int_zero = rec.decode(0)
        expected_int_zero = 0

        decoded_float = rec.decode(6.6)
        expected_float = 6.6

        decoded_float_zero = rec.decode(0.0)
        expected_float_zero = 0.0

        decoded_bool = rec.decode(True)
        expected_bool = True

        decoded_bool2 = rec.decode(False)
        expected_bool2 = False

        self.assertEqual(decoded_none, expected_none)
        self.assertEqual(type(decoded_none), type(expected_none))

        self.assertEqual(decoded_int, expected_int)
        self.assertEqual(type(decoded_int), type(expected_int))
        self.assertEqual(decoded_int_zero, expected_int_zero)
        self.assertEqual(type(decoded_int_zero), type(expected_int_zero))

        self.assertEqual(decoded_float, expected_float)
        self.assertEqual(type(decoded_float), type(expected_float))
        self.assertEqual(decoded_float_zero, expected_float_zero)
        self.assertEqual(type(decoded_float_zero), type(expected_float_zero))

        self.assertEqual(decoded_bool, expected_bool)
        self.assertEqual(type(decoded_bool), type(expected_bool))
        self.assertEqual(decoded_bool2, expected_bool2)
        self.assertEqual(type(decoded_bool2), type(expected_bool2))

    def test_encode_basic_types(self):
        """ CorbaRecoder encodes basic types to corba correctly . """
        rec = self.recoder_class("utf-8")

        encoded_none = rec.encode(None)
        expected_none = None

        encoded_int = rec.encode(6)
        expected_int = 6

        encoded_int_zero = rec.encode(0)
        expected_int_zero = 0

        encoded_float = rec.encode(6.6)
        expected_float = 6.6

        encoded_float_zero = rec.encode(0.0)
        expected_float_zero = 0.0

        encoded_bool = rec.encode(True)
        expected_bool = True

        encoded_bool2 = rec.encode(False)
        expected_bool2 = False

        self.assertEqual(encoded_none, expected_none)
        self.assertEqual(type(encoded_none), type(expected_none))

        self.assertEqual(encoded_int, expected_int)
        self.assertEqual(type(encoded_int), type(expected_int))
        self.assertEqual(encoded_int_zero, expected_int_zero)
        self.assertEqual(type(encoded_int_zero), type(expected_int_zero))

        self.assertEqual(encoded_float, expected_float)
        self.assertEqual(type(encoded_float), type(expected_float))
        self.assertEqual(encoded_float_zero, expected_float_zero)
        self.assertEqual(type(encoded_float_zero), type(expected_float_zero))

        self.assertEqual(encoded_bool, expected_bool)
        self.assertEqual(type(encoded_bool), type(expected_bool))
        self.assertEqual(encoded_bool2, expected_bool2)
        self.assertEqual(type(encoded_bool2), type(expected_bool2))

    def test_decode_strings(self):
        rec = self.recoder_class("utf-8")

        decoded_bytes = rec.decode(b'string')
        if six.PY2:
            expected_bytes = 'string'
        else:
            assert six.PY3
            expected_bytes = b'string'

        decoded_bytes_empty = rec.decode(b'')
        if six.PY2:
            expected_bytes_empty = ''
        else:
            assert six.PY3
            expected_bytes_empty = b''

        decoded_text = rec.decode('test \u010d\u0165')
        expected_text = 'test \u010d\u0165'

        decoded_bytes_chars = rec.decode(b'test \xc4\x8d\xc5\xa5')
        if six.PY2:
            expected_bytes_chars = 'test \u010d\u0165'
        else:
            assert six.PY3
            expected_bytes_chars = b'test \xc4\x8d\xc5\xa5'

        self.assertEqual(decoded_bytes, expected_bytes)
        self.assertEqual(type(decoded_bytes), type(expected_bytes))
        self.assertEqual(decoded_bytes_empty, expected_bytes_empty)
        self.assertEqual(type(decoded_bytes_empty), type(expected_bytes_empty))
        self.assertEqual(decoded_bytes_chars, expected_bytes_chars)
        self.assertEqual(type(decoded_bytes_chars), type(expected_bytes_chars))

        self.assertEqual(decoded_text, expected_text)
        self.assertEqual(type(decoded_text), type(expected_text))

    def test_encode_strings(self):
        rec = self.recoder_class("utf-8")

        encoded_bytes = rec.encode('string')
        if six.PY2:
            expected_bytes = b'string'
        else:
            assert six.PY3
            expected_bytes = 'string'

        encoded_bytes_empty = rec.encode('')
        if six.PY2:
            expected_bytes_empty = b''
        else:
            assert six.PY3
            expected_bytes_empty = ''

        encoded_bytes = rec.encode(b'unicode')
        expected_bytes = b'unicode'

        encoded_text_chars = rec.encode('test \u010d\u0165')
        if six.PY2:
            expected_text_chars = b'test \xc4\x8d\xc5\xa5'
        else:
            assert six.PY3
            expected_text_chars = 'test \u010d\u0165'

        self.assertEqual(encoded_bytes, expected_bytes)
        self.assertEqual(type(encoded_bytes), type(expected_bytes))
        self.assertEqual(encoded_bytes_empty, expected_bytes_empty)
        self.assertEqual(type(encoded_bytes_empty), type(expected_bytes_empty))

        self.assertEqual(encoded_bytes, expected_bytes)
        self.assertEqual(type(encoded_bytes), type(expected_bytes))
        self.assertEqual(encoded_text_chars, expected_text_chars)
        self.assertEqual(type(encoded_text_chars), type(expected_text_chars))

    def test_decode_iter_types(self):
        """ CorbaRecoder decodes iter types to python correctly . """
        rec = self.recoder_class("utf-8")

        original_tuple = (b'string', b'unicode', (b'tuple', 4), None, True)
        original_tuple_copy = copy.deepcopy(original_tuple)
        decoded_tuple = rec.decode(original_tuple)
        if six.PY2:
            expected_tuple = ('string', 'unicode', ('tuple', 4), None, True)
        else:
            assert six.PY3
            expected_tuple = (b'string', b'unicode', (b'tuple', 4), None, True)

        original_list = [b'string', b'unicode', [b'list', 4], None, True]
        original_list_copy = copy.deepcopy(original_list)
        decoded_list = rec.decode(original_list)
        if six.PY2:
            expected_list = ['string', 'unicode', ['list', 4], None, True]
        else:
            assert six.PY3
            expected_list = [b'string', b'unicode', [b'list', 4], None, True]

        self.assertEqual(original_tuple, original_tuple_copy)
        self.assertEqual(type(original_tuple), type(original_tuple_copy))
        self.assertEqual(original_tuple[2][0], original_tuple_copy[2][0])
        self.assertEqual(type(original_tuple[2][0]), type(original_tuple_copy[2][0]))

        self.assertEqual(decoded_tuple, expected_tuple)
        self.assertEqual(type(decoded_tuple), type(expected_tuple))
        self.assertEqual(decoded_tuple[2][0], expected_tuple[2][0])
        self.assertEqual(type(decoded_tuple[2][0]), type(expected_tuple[2][0]))

        self.assertEqual(original_list, original_list_copy)
        self.assertEqual(type(original_list), type(original_list_copy))
        self.assertEqual(original_list[2][0], original_list_copy[2][0])
        self.assertEqual(type(original_list[2][0]), type(original_list_copy[2][0]))

        self.assertEqual(decoded_list, expected_list)
        self.assertEqual(type(decoded_list), type(expected_list))
        self.assertEqual(decoded_list[2][0], expected_list[2][0])
        self.assertEqual(type(decoded_list[2][0]), type(expected_list[2][0]))

    def test_encode_iter_types(self):
        """ CorbaRecoder encodes iter types to corba correctly . """
        rec = self.recoder_class("utf-8")

        original_tuple = ('string', 'unicode', ('tuple', 4), None, True)
        original_tuple_copy = copy.deepcopy(original_tuple)
        encoded_tuple = rec.encode(('string', 'unicode', ('tuple', 4), None, True))
        if six.PY2:
            expected_tuple = (b'string', b'unicode', (b'tuple', 4), None, True)
        else:
            assert six.PY3
            expected_tuple = ('string', 'unicode', ('tuple', 4), None, True)

        original_list = ['string', 'unicode', ['list', 4], None, True]
        original_list_copy = copy.deepcopy(original_list)
        encoded_list = rec.encode(['string', 'unicode', ['list', 4], None, True])
        if six.PY2:
            expected_list = [b'string', b'unicode', [b'list', 4], None, True]
        else:
            assert six.PY3
            expected_list = ['string', 'unicode', ['list', 4], None, True]

        self.assertEqual(original_tuple, original_tuple_copy)
        self.assertEqual(type(original_tuple), type(original_tuple_copy))
        self.assertEqual(original_tuple[2][0], original_tuple_copy[2][0])
        self.assertEqual(type(original_tuple[2][0]), type(original_tuple_copy[2][0]))

        self.assertEqual(encoded_tuple, expected_tuple)
        self.assertEqual(type(encoded_tuple), type(expected_tuple))
        self.assertEqual(encoded_tuple[2][0], expected_tuple[2][0])
        self.assertEqual(type(encoded_tuple[2][0]), type(expected_tuple[2][0]))

        self.assertEqual(original_list, original_list_copy)
        self.assertEqual(type(original_list), type(original_list_copy))
        self.assertEqual(original_list[2][0], original_list_copy[2][0])
        self.assertEqual(type(original_list[2][0]), type(original_list_copy[2][0]))

        self.assertEqual(encoded_list, expected_list)
        self.assertEqual(type(encoded_list), type(expected_list))
        self.assertEqual(encoded_list[2][0], expected_list[2][0])
        self.assertEqual(type(encoded_list[2][0]), type(expected_list[2][0]))

    def test_decode_enum_item(self):
        recoder = self.recoder_class("utf-8")
        self.assertEqual(recoder.decode(TEST_ENUM_ITEM), TEST_ENUM_ITEM)

    def test_encode_enum_item(self):
        recoder = self.recoder_class("utf-8")
        self.assertEqual(recoder.encode(TEST_ENUM_ITEM), TEST_ENUM_ITEM)

    def test_decode_struct(self):
        """ CorbaRecoder decodes corba entity to python correctly . """
        rec = self.recoder_class("utf-8")
        reg = SampleCorbaStruct(
            id=19, ico=b'', dic=b'', varSymb=b'', vat=False,
            handle=b'NEW REG', name=b'name 1', organization=b'',
            street1=b'chars \xc4\x8d\xc5\xa5', street2=b'', street3=b'', city=b'', stateorprovince=b'state',
            postalcode=b'', country=b'CZ', telephone=b'', fax=b'', email=b'', url=b'',
            credit=b'0.00', unspec_credit=b'0.00', access=[], zones=[], hidden=False)
        reg_copy = copy.deepcopy(reg)
        if six.PY2:
            expected = SampleCorbaStruct(
                id=19, ico='', dic='', varSymb='', vat=False,
                handle='NEW REG', name='name 1', organization='',
                street1='chars \u010d\u0165', street2='', street3='', city='', stateorprovince='state',
                postalcode='', country='CZ', telephone='', fax='', email='', url='',
                credit='0.00', unspec_credit='0.00', access=[], zones=[], hidden=False)
        else:
            assert six.PY3
            expected = SampleCorbaStruct(
                id=19, ico=b'', dic=b'', varSymb=b'', vat=False,
                handle=b'NEW REG', name=b'name 1', organization=b'',
                street1=b'chars \xc4\x8d\xc5\xa5', street2=b'', street3=b'', city=b'', stateorprovince=b'state',
                postalcode=b'', country=b'CZ', telephone=b'', fax=b'', email=b'', url=b'',
                credit=b'0.00', unspec_credit=b'0.00', access=[], zones=[], hidden=False)

        decoded_reg = rec.decode(reg)

        self.assertEqual(reg.__dict__, reg_copy.__dict__)
        self.assertEqual(type(reg.__dict__['street1']), type(reg_copy.__dict__['street1']))
        self.assertEqual(type(reg.__dict__['vat']), type(reg_copy.__dict__['vat']))
        self.assertEqual(type(reg.__dict__['access']), type(reg_copy.__dict__['access']))

        self.assertEqual(decoded_reg.__dict__, expected.__dict__)
        self.assertEqual(type(decoded_reg.__dict__['street1']), type(expected.__dict__['street1']))
        self.assertEqual(type(decoded_reg.__dict__['vat']), type(expected.__dict__['vat']))
        self.assertEqual(type(decoded_reg.__dict__['access']), type(expected.__dict__['access']))

    def test_encode_struct(self):
        """ CorbaRecoder encodes python entity to corba correctly """
        rec = self.recoder_class("utf-8")
        reg = SampleCorbaStruct(
            id=19, ico='', dic='', varSymb='', vat=False,
            handle='NEW REG', name='name 1', organization='',
            street1='chars \u010d\u0165', street2='', street3='', city='', stateorprovince='state',
            postalcode='', country='CZ', telephone='', fax='', email='', url='',
            credit='0.00', unspec_credit='0.00', access=[], zones=[], hidden=False)
        reg_copy = copy.deepcopy(reg)
        if six.PY2:
            expected = SampleCorbaStruct(
                id=19, ico=b'', dic=b'', varSymb=b'', vat=False,
                handle=b'NEW REG', name=b'name 1', organization=b'',
                street1=b'chars \xc4\x8d\xc5\xa5', street2=b'', street3=b'', city=b'', stateorprovince=b'state',
                postalcode=b'', country=b'CZ', telephone=b'', fax=b'', email=b'', url=b'',
                credit=b'0.00', unspec_credit=b'0.00', access=[], zones=[], hidden=False)
        else:
            assert six.PY3
            expected = SampleCorbaStruct(
                id=19, ico='', dic='', varSymb='', vat=False,
                handle='NEW REG', name='name 1', organization='',
                street1='chars \u010d\u0165', street2='', street3='', city='', stateorprovince='state',
                postalcode='', country='CZ', telephone='', fax='', email='', url='',
                credit='0.00', unspec_credit='0.00', access=[], zones=[], hidden=False)

        encoded_entity = rec.encode(reg)

        self.assertEqual(reg.__dict__, reg_copy.__dict__)
        self.assertEqual(type(reg.__dict__['street1']), type(reg_copy.__dict__['street1']))
        self.assertEqual(type(reg.__dict__['vat']), type(reg_copy.__dict__['vat']))
        self.assertEqual(type(reg.__dict__['access']), type(reg_copy.__dict__['access']))

        self.assertEqual(encoded_entity.__dict__, expected.__dict__)
        self.assertEqual(type(encoded_entity.__dict__['street1']), type(expected.__dict__['street1']))
        self.assertEqual(type(encoded_entity.__dict__['vat']), type(expected.__dict__['vat']))
        self.assertEqual(type(encoded_entity.__dict__['access']), type(expected.__dict__['access']))

    @unittest.skipUnless(six.PY2, "This tests requires python 2 only")
    def test_decode_nested_struct_py2(self):
        rec = self.recoder_class("utf-8")
        obj = NodeStruct(b'A', NodeStruct(b'B', NodeStruct(b'C', None)))

        output = rec.decode(obj)

        # Check output
        self.assertEqual(output.text, 'A')
        self.assertIsInstance(output.text, six.text_type)
        self.assertIsInstance(output.inner, NodeStruct)
        self.assertEqual(output.inner.text, 'B')
        self.assertIsInstance(output.inner.text, six.text_type)
        self.assertIsInstance(output.inner.inner, NodeStruct)
        self.assertEqual(output.inner.inner.text, 'C')
        self.assertIsInstance(output.inner.inner.text, six.text_type)
        self.assertIsNone(output.inner.inner.inner)

        # Check original object
        self.assertEqual(obj.text, b'A')
        self.assertIsInstance(obj.text, six.binary_type)
        self.assertIsInstance(obj.inner, NodeStruct)
        self.assertEqual(obj.inner.text, b'B')
        self.assertIsInstance(obj.inner.text, six.binary_type)
        self.assertIsInstance(obj.inner.inner, NodeStruct)
        self.assertEqual(obj.inner.inner.text, b'C')
        self.assertIsInstance(obj.inner.inner.text, six.binary_type)
        self.assertIsNone(obj.inner.inner.inner)

    @unittest.skipUnless(six.PY3, "This tests requires python 3 only")
    def test_decode_nested_struct(self):
        rec = self.recoder_class("utf-8")
        obj = NodeStruct('A', NodeStruct('B', NodeStruct('C', None)))

        output = rec.decode(obj)

        # Check output
        self.assertEqual(output.text, 'A')
        self.assertIsInstance(output.inner, NodeStruct)
        self.assertEqual(output.inner.text, 'B')
        self.assertIsInstance(output.inner.inner, NodeStruct)
        self.assertEqual(output.inner.inner.text, 'C')
        self.assertIsNone(output.inner.inner.inner)

        # Check original object
        self.assertEqual(obj.text, 'A')
        self.assertIsInstance(obj.inner, NodeStruct)
        self.assertEqual(obj.inner.text, 'B')
        self.assertIsInstance(obj.inner.inner, NodeStruct)
        self.assertEqual(obj.inner.inner.text, 'C')
        self.assertIsNone(obj.inner.inner.inner)

    @unittest.skipUnless(six.PY2, "This tests requires python 2 only")
    def test_encode_nested_struct_py2(self):
        rec = self.recoder_class("utf-8")
        obj = NodeStruct('A', NodeStruct('B', NodeStruct('C', None)))

        output = rec.encode(obj)

        # Check output
        self.assertEqual(output.text, b'A')
        self.assertIsInstance(output.text, six.binary_type)
        self.assertIsInstance(output.inner, NodeStruct)
        self.assertEqual(output.inner.text, b'B')
        self.assertIsInstance(output.inner.text, six.binary_type)
        self.assertIsInstance(output.inner.inner, NodeStruct)
        self.assertEqual(output.inner.inner.text, b'C')
        self.assertIsInstance(output.inner.inner.text, six.binary_type)
        self.assertIsNone(output.inner.inner.inner)

        # Check original object
        self.assertEqual(obj.text, 'A')
        self.assertIsInstance(obj.text, six.text_type)
        self.assertIsInstance(obj.inner, NodeStruct)
        self.assertEqual(obj.inner.text, 'B')
        self.assertIsInstance(obj.inner.text, six.text_type)
        self.assertIsInstance(obj.inner.inner, NodeStruct)
        self.assertEqual(obj.inner.inner.text, 'C')
        self.assertIsInstance(obj.inner.inner.text, six.text_type)
        self.assertIsNone(obj.inner.inner.inner)

    @unittest.skipUnless(six.PY3, "This tests requires python 3 only")
    def test_encode_nested_struct(self):
        rec = self.recoder_class("utf-8")
        obj = NodeStruct('A', NodeStruct('B', NodeStruct('C', None)))

        output = rec.encode(obj)

        # Check output
        self.assertEqual(output.text, 'A')
        self.assertIsInstance(output.inner, NodeStruct)
        self.assertEqual(output.inner.text, 'B')
        self.assertIsInstance(output.inner.inner, NodeStruct)
        self.assertEqual(output.inner.inner.text, 'C')
        self.assertIsNone(output.inner.inner.inner)

        # Check original object
        self.assertEqual(obj.text, 'A')
        self.assertIsInstance(obj.inner, NodeStruct)
        self.assertEqual(obj.inner.text, 'B')
        self.assertIsInstance(obj.inner.inner, NodeStruct)
        self.assertEqual(obj.inner.inner.text, 'C')
        self.assertIsNone(obj.inner.inner.inner)

    def test_decode_other(self):
        """ Decoding object raise error """
        rec = self.recoder_class("utf-8")
        reg = object()
        self.assertRaises(ValueError, rec.decode, reg)

    def test_encode_other(self):
        """ Encoding object raise error """
        rec = self.recoder_class("utf-8")
        reg = object()
        self.assertRaises(ValueError, rec.encode, reg)

    def test_sanity_dec_enc(self):
        """ encode(decode(obj)) is equal to obj. """
        rec = self.recoder_class("utf-8")
        reg = SampleCorbaStruct(
            id=19, ico=b'', dic=b'', varSymb=b'', vat=False,
            handle=b'NEW REG', name=b'name 1', organization=b'',
            street1=b'chars \xc4\x8d\xc5\xa5', street2=b'', street3=b'', city=b'', stateorprovince=b'state',
            postalcode=b'', country=b'CZ', telephone=b'', fax=b'', email=b'', url=b'',
            credit=b'0.00', unspec_credit=b'0.00', access=[], zones=[], hidden=False)
        expected = SampleCorbaStruct(
            id=19, ico=b'', dic=b'', varSymb=b'', vat=False,
            handle=b'NEW REG', name=b'name 1', organization=b'',
            street1=b'chars \xc4\x8d\xc5\xa5', street2=b'', street3=b'', city=b'', stateorprovince=b'state',
            postalcode=b'', country=b'CZ', telephone=b'', fax=b'', email=b'', url=b'',
            credit=b'0.00', unspec_credit=b'0.00', access=[], zones=[], hidden=False)

        res = rec.encode(rec.decode(reg))

        self.assertEqual(res.__dict__, expected.__dict__)
        self.assertEqual(type(res.__dict__['street1']), type(expected.__dict__['street1']))
        self.assertEqual(type(res.__dict__['vat']), type(expected.__dict__['vat']))
        self.assertEqual(type(res.__dict__['access']), type(expected.__dict__['access']))

    def test_sanity_enc_dec(self):
        """ decode(encode(obj)) has equal types to obj. """
        rec = self.recoder_class("utf-8")
        reg = SampleCorbaStruct(
            id=19, ico='', dic='', varSymb='', vat=False,
            handle='NEW REG', name='name 1', organization='',
            street1='chars \u010d\u0165', street2='', street3='', city='', stateorprovince='state',
            postalcode='', country='CZ', telephone='', fax='', email='', url='',
            credit='0.00', unspec_credit='0.00', access=[], zones=[], hidden=False)
        expected = SampleCorbaStruct(
            id=19, ico='', dic='', varSymb='', vat=False,
            handle='NEW REG', name='name 1', organization='',
            street1='chars \u010d\u0165', street2='', street3='', city='', stateorprovince='state',
            postalcode='', country='CZ', telephone='', fax='', email='', url='',
            credit='0.00', unspec_credit='0.00', access=[], zones=[], hidden=False)

        res = rec.decode(rec.encode(reg))

        self.assertEqual(res.__dict__, expected.__dict__)
        self.assertEqual(type(res.__dict__['street1']), type(expected.__dict__['street1']))
        self.assertEqual(type(res.__dict__['vat']), type(expected.__dict__['vat']))
        self.assertEqual(type(res.__dict__['access']), type(expected.__dict__['access']))
