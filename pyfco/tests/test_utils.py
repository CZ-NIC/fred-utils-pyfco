"""
Tests for `pyfco.utils`.
"""
from __future__ import unicode_literals

import unittest

from mock import call, sentinel
from omniORB import StructBase

from pyfco.utils import CorbaAssertMixin


class OldStyleClass:
    def __eq__(self, other):
        return True


class SimpleStruct(StructBase):
    """Simple corba structure for testing."""

    def __init__(self, value):
        self.value = value


class OtherStruct(StructBase):
    """Simple corba structure for testing."""

    def __init__(self, value):
        self.value = value


class CustomStruct(SimpleStruct):
    """Simple corba structure for testing."""


class OtherCustomStruct(SimpleStruct):
    """Simple corba structure for testing."""


def assert_other_custom_struct(first, second, msg):
    assert False, "Other custom comparison error"


class TestCorbaAssertMixin(CorbaAssertMixin, unittest.TestCase):
    """
    Test that corba structures are compared correctly.
    """
    corba_equality_funcs = {CustomStruct: 'assertCustomEqual',
                            OtherCustomStruct: assert_other_custom_struct}

    def test_other_old_style(self):
        # Test other old style classes still work
        self.assertEqual(OldStyleClass(), OldStyleClass())

    def test_struct_mismatch(self):
        first = SimpleStruct(sentinel.value)
        second = OtherStruct(sentinel.value)
        msg = "SimpleStruct.* != .*OtherStruct"
        with self.assertRaisesRegexp(self.failureException, msg):
            self.assertEqual(first, second)

    def test_simple_struct(self):
        struct_1 = SimpleStruct(sentinel.value)
        struct_2 = SimpleStruct(sentinel.value)
        struct_3 = SimpleStruct(sentinel.another)

        self.assertEqual(struct_1, struct_1)
        self.assertEqual(struct_1, struct_2)
        msg = "SimpleStruct.* != .*SimpleStruct.*"
        with self.assertRaisesRegexp(self.failureException, msg):
            self.assertEqual(struct_1, struct_3)

    def test_nested_struct(self):
        struct_1 = SimpleStruct(SimpleStruct(sentinel.value))
        struct_2 = SimpleStruct(SimpleStruct(sentinel.value))
        struct_3 = SimpleStruct(SimpleStruct(sentinel.another))
        self.assertEqual(struct_1, struct_1)
        self.assertEqual(struct_1, struct_2)

        msg = "SimpleStruct.* != .*SimpleStruct.*"
        with self.assertRaisesRegexp(self.failureException, msg):
            self.assertEqual(struct_1, struct_3)

    def test_corba_calls_equal(self):
        calls_1 = [call.function(SimpleStruct(sentinel.value))]
        calls_2 = [call.function(SimpleStruct(sentinel.value))]
        calls_3 = [call.other_function(SimpleStruct(sentinel.value))]
        calls_4 = [call.function(SimpleStruct(sentinel.another))]

        self.assertCorbaCallsEqual(calls_1, calls_1)
        self.assertCorbaCallsEqual(calls_1, calls_2)
        msg = r"\[call.function\(.*SimpleStruct.*\)\] != \[call.other_function\(.*SimpleStruct.*\)\]"
        with self.assertRaisesRegexp(self.failureException, msg):
            self.assertCorbaCallsEqual(calls_1, calls_3)
        msg = r"\[call.function\(.*SimpleStruct.*\)\] != \[call.function\(.*SimpleStruct.*\)\]"
        with self.assertRaisesRegexp(self.failureException, msg):
            self.assertCorbaCallsEqual(calls_1, calls_4)

        calls_kw1 = [call.function(key=SimpleStruct(sentinel.value))]
        calls_kw2 = [call.function(key=SimpleStruct(sentinel.value))]
        calls_kw3 = [call.function(other_key=SimpleStruct(sentinel.value))]
        calls_kw4 = [call.function(key=SimpleStruct(sentinel.another))]

        self.assertCorbaCallsEqual(calls_kw1, calls_kw1)
        self.assertCorbaCallsEqual(calls_kw1, calls_kw2)
        msg = r"\[call.function\(key=.*SimpleStruct.*\)\] != \[call.function\(other_key=.*SimpleStruct.*\)\]"
        with self.assertRaisesRegexp(self.failureException, msg):
            self.assertCorbaCallsEqual(calls_kw1, calls_kw3)
        msg = r"\[call.function\(key=.*SimpleStruct.*\)\] != \[call.function\(key=.*SimpleStruct.*\)\]"
        with self.assertRaisesRegexp(self.failureException, msg):
            self.assertCorbaCallsEqual(calls_kw1, calls_kw4)

        # Args doesn't match kwargs
        msg = r"\[call.function\(.*SimpleStruct.*\)\] != \[call.function\(key=.*SimpleStruct.*\)\]"
        with self.assertRaisesRegexp(self.failureException, msg):
            self.assertCorbaCallsEqual(calls_1, calls_kw1)

    def assertCustomEqual(self, first, other, msg):
        self.fail("Custom comparison error")

    def test_custom_asserter(self):
        msg = "Custom comparison error"
        with self.assertRaisesRegexp(self.failureException, msg):
            self.assertEqual(CustomStruct(sentinel.value), CustomStruct(sentinel.value))

        msg = "Other custom comparison error"
        with self.assertRaisesRegexp(self.failureException, msg):
            self.assertEqual(OtherCustomStruct(sentinel.value), OtherCustomStruct(sentinel.value))
