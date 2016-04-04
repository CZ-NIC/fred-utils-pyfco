import copy
import unittest

from omniORB import StructBase

from pyfco import corbarecoder as recoder


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


class TestCorbaRecoder(unittest.TestCase):

    recoder_class = recoder.CorbaRecoder

    def test_create(self):
        """ CorbaRecoder is created with supported encoding. """
        rec = self.recoder_class("utf-8")
        self.assertIsNotNone(rec)

    def test_create_wrong_encoding(self):
        """ CorbaRecoder raises error for unsupported encoding. """
        self.assertRaises(recoder.UnsupportedEncodingError, self.recoder_class, "invalid coding")

    def test_decode_basic_types(self):
        """ CorbaRecoder decodes basic types to python correctly . """
        rec = self.recoder_class("utf-8")

        decoded_str = rec.decode('string')
        expected_str = u'string'

        decoded_str_empty = rec.decode('')
        expected_str_empty = u''

        decoded_str_chars = rec.decode('test \xc4\x8d\xc5\xa5')
        expected_str_chars = u'test \u010d\u0165'

        decoded_unicode = rec.decode(u'unicode')
        expected_unicode = u'unicode'

        decoded_unicode_empty = rec.decode(u'')
        expected_unicode_empty = u''

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

        self.assertEqual(decoded_str, expected_str)
        self.assertEqual(type(decoded_str), type(expected_str))
        self.assertEqual(decoded_str_empty, expected_str_empty)
        self.assertEqual(type(decoded_str_empty), type(expected_str_empty))
        self.assertEqual(decoded_str_chars, expected_str_chars)
        self.assertEqual(type(decoded_str_chars), type(expected_str_chars))

        self.assertEqual(decoded_unicode, expected_unicode)
        self.assertEqual(type(decoded_unicode), type(expected_unicode))
        self.assertEqual(decoded_unicode_empty, expected_unicode_empty)
        self.assertEqual(type(decoded_unicode_empty), type(expected_unicode_empty))

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

        encoded_str = rec.encode('string')
        expected_str = 'string'

        encoded_str_empty = rec.encode('')
        expected_str_empty = ''

        encoded_unicode = rec.encode(u'unicode')
        expected_unicode = 'unicode'

        encoded_unicode_empty = rec.encode(u'')
        expected_unicode_empty = ''

        encoded_unicode_chars = rec.encode(u'test \u010d\u0165')
        expected_unicode_chars = 'test \xc4\x8d\xc5\xa5'

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

        self.assertEqual(encoded_str, expected_str)
        self.assertEqual(type(encoded_str), type(expected_str))
        self.assertEqual(encoded_str_empty, expected_str_empty)
        self.assertEqual(type(encoded_str_empty), type(expected_str_empty))

        self.assertEqual(encoded_unicode, expected_unicode)
        self.assertEqual(type(encoded_unicode), type(expected_unicode))
        self.assertEqual(encoded_unicode_empty, expected_unicode_empty)
        self.assertEqual(type(encoded_unicode_empty), type(expected_unicode_empty))
        self.assertEqual(encoded_unicode_chars, expected_unicode_chars)
        self.assertEqual(type(encoded_unicode_chars), type(expected_unicode_chars))

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

    def test_decode_iter_types(self):
        """ CorbaRecoder decodes iter types to python correctly . """
        rec = self.recoder_class("utf-8")

        original_tuple = ('string', u'unicode', ('tuple', 4), None, True)
        original_tuple_copy = copy.deepcopy(original_tuple)
        decoded_tuple = rec.decode(original_tuple)
        expected_tuple = (u'string', u'unicode', (u'tuple', 4), None, True)

        original_list = ['string', u'unicode', ['list', 4], None, True]
        original_list_copy = copy.deepcopy(original_list)
        decoded_list = rec.decode(original_list)
        expected_list = [u'string', u'unicode', [u'list', 4], None, True]

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

        original_tuple = ('string', u'unicode', (u'tuple', 4), None, True)
        original_tuple_copy = copy.deepcopy(original_tuple)
        encoded_tuple = rec.encode(('string', u'unicode', (u'tuple', 4), None, True))
        expected_tuple = ('string', 'unicode', ('tuple', 4), None, True)

        original_list = ['string', u'unicode', [u'list', 4], None, True]
        original_list_copy = copy.deepcopy(original_list)
        encoded_list = rec.encode(['string', u'unicode', [u'list', 4], None, True])
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

    def test_decode_struct(self):
        """ CorbaRecoder decodes corba entity to python correctly . """
        rec = self.recoder_class("utf-8")
        reg = SampleCorbaStruct(
            id=19, ico='', dic='', varSymb='', vat=False,
            handle='NEW REG', name='name 1', organization='',
            street1='chars \xc4\x8d\xc5\xa5', street2='', street3='', city='', stateorprovince='state',
            postalcode='', country='CZ', telephone='', fax='', email='', url='',
            credit='0.00', unspec_credit='0.00', access=[], zones=[], hidden=False)
        reg_copy = copy.deepcopy(reg)
        expected = SampleCorbaStruct(
            id=19, ico=u'', dic=u'', varSymb=u'', vat=False,
            handle=u'NEW REG', name=u'name 1', organization=u'',
            street1=u'chars \u010d\u0165', street2=u'', street3=u'', city=u'', stateorprovince=u'state',
            postalcode=u'', country=u'CZ', telephone=u'', fax=u'', email=u'', url=u'',
            credit=u'0.00', unspec_credit=u'0.00', access=[], zones=[], hidden=False)

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
            id=19, ico=u'', dic=u'', varSymb=u'', vat=False,
            handle=u'NEW REG', name=u'name 1', organization=u'',
            street1=u'chars \u010d\u0165', street2=u'', street3=u'', city=u'', stateorprovince=u'state',
            postalcode=u'', country=u'CZ', telephone=u'', fax=u'', email=u'', url=u'',
            credit=u'0.00', unspec_credit=u'0.00', access=[], zones=[], hidden=False)
        reg_copy = copy.deepcopy(reg)
        expected = SampleCorbaStruct(
            id=19, ico='', dic='', varSymb='', vat=False,
            handle='NEW REG', name='name 1', organization='',
            street1='chars \xc4\x8d\xc5\xa5', street2='', street3='', city='', stateorprovince='state',
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

    class Foo():
        """ Fake class for encoding testing. """
        def __init__(self, a, b, c):
            self.a, self.b, self.c = a, b, c

        def __str__(self):

            return "Foo(%s, %s, %s)" % (self.a, self.b, self.c)

        def __repr__(self):
            return self.__str__()

        def __eq__(self, obj):
            """ Equality is defined so that we can assert it easier"""
            return (self.a == obj.a and
                    self.b == obj.b and
                    self.c == obj.c)

    class Bar(Foo):
        """ Fake class for encoding testing. """
        def __str__(self):
            return "Bar(%s, %s, %s)" % (self.a, self.b, self.c)

    def test_encode_double_nested_oldstyle_class_attrs(self):
        """ Nested class attrs gets encoded OK.
            Note: We're using old-style classes, because that's what omniORBpy
            does. """
        rec = self.recoder_class("utf-8")
        p_ent = TestCorbaRecoder.Foo(
            1, TestCorbaRecoder.Bar(
                2, TestCorbaRecoder.Bar(3, None, u"5"),
                6.0),
            0)
        expected = TestCorbaRecoder.Foo(
            1, TestCorbaRecoder.Bar(
                2, TestCorbaRecoder.Bar(3, None, "5"),
                6.0),
            0)
        res = rec.encode(p_ent)

        self.assertEqual(expected, res)
        self.assertEqual(type(res.b.b.b), type(expected.b.b.b))
        self.assertEqual(type(res.b.b.c), type(expected.b.b.c))
        self.assertEqual(type(res.b.c), type(expected.b.c))

    def test_decode_double_nested_oldstyle_class_types(self):
        """ Nested class types gets encoded OK.
            Note: We're using old-style classes, because that's what omniORBpy
            does. """
        rec = self.recoder_class("utf-8")
        p_ent = TestCorbaRecoder.Foo(
            1, TestCorbaRecoder.Bar(
                2, TestCorbaRecoder.Bar(3, None, "5"),
                6.0),
            0)
        expected = TestCorbaRecoder.Foo(
            1, TestCorbaRecoder.Bar(
                2, TestCorbaRecoder.Bar(3, None, u"5"),
                6.0),
            0)
        res = rec.decode(p_ent)

        self.assertEqual(expected, res)
        self.assertEqual(type(res.b.b.b), type(expected.b.b.b))
        self.assertEqual(type(res.b.b.c), type(expected.b.b.c))
        self.assertEqual(type(res.b.c), type(expected.b.c))

    def test_sanity_dec_enc(self):
        """ encode(decode(obj)) is equal to obj. """
        rec = self.recoder_class("utf-8")
        reg = SampleCorbaStruct(
            id=19, ico='', dic='', varSymb='', vat=False,
            handle='NEW REG', name='name 1', organization='',
            street1='chars \xc4\x8d\xc5\xa5', street2='', street3='', city='', stateorprovince='state',
            postalcode='', country='CZ', telephone='', fax='', email='', url='',
            credit='0.00', unspec_credit='0.00', access=[], zones=[], hidden=False)
        expected = SampleCorbaStruct(
            id=19, ico='', dic='', varSymb='', vat=False,
            handle='NEW REG', name='name 1', organization='',
            street1='chars \xc4\x8d\xc5\xa5', street2='', street3='', city='', stateorprovince='state',
            postalcode='', country='CZ', telephone='', fax='', email='', url='',
            credit='0.00', unspec_credit='0.00', access=[], zones=[], hidden=False)

        res = rec.encode(rec.decode(reg))

        self.assertEqual(res.__dict__, expected.__dict__)
        self.assertEqual(type(res.__dict__['street1']), type(expected.__dict__['street1']))
        self.assertEqual(type(res.__dict__['vat']), type(expected.__dict__['vat']))
        self.assertEqual(type(res.__dict__['access']), type(expected.__dict__['access']))

    def test_sanity_enc_dec(self):
        """ decode(encode(obj)) has equal types to obj. """
        rec = self.recoder_class("utf-8")
        reg = SampleCorbaStruct(
            id=19, ico=u'', dic=u'', varSymb=u'', vat=False,
            handle=u'NEW REG', name=u'name 1', organization=u'',
            street1=u'chars \u010d\u0165', street2=u'', street3=u'', city=u'', stateorprovince=u'state',
            postalcode=u'', country=u'CZ', telephone=u'', fax=u'', email=u'', url=u'',
            credit=u'0.00', unspec_credit=u'0.00', access=[], zones=[], hidden=False)
        expected = SampleCorbaStruct(
            id=19, ico=u'', dic=u'', varSymb=u'', vat=False,
            handle=u'NEW REG', name=u'name 1', organization=u'',
            street1=u'chars \u010d\u0165', street2=u'', street3=u'', city=u'', stateorprovince=u'state',
            postalcode=u'', country=u'CZ', telephone=u'', fax=u'', email=u'', url=u'',
            credit=u'0.00', unspec_credit=u'0.00', access=[], zones=[], hidden=False)

        res = rec.decode(rec.encode(reg))

        self.assertEqual(res.__dict__, expected.__dict__)
        self.assertEqual(type(res.__dict__['street1']), type(expected.__dict__['street1']))
        self.assertEqual(type(res.__dict__['vat']), type(expected.__dict__['vat']))
        self.assertEqual(type(res.__dict__['access']), type(expected.__dict__['access']))
