# -*- coding: utf-8 -*-
"""
Tests for `pyfco.client` module
"""
import logging
import unittest
from logging.handlers import BufferingHandler

from mock import Mock, call, patch, sentinel
from omniORB import CORBA

from pyfco.client import CorbaClient, CorbaClientProxy, sane_repr
from pyfco.corbarecoder import CorbaRecoder


class TestSaneRepr(unittest.TestCase):
    """
    Test `sane_repr` utility function.
    """
    def test_sane_repr(self):
        self.assertEqual(sane_repr(None, 1024), "None")
        self.assertEqual(sane_repr(10562, 1024), "10562")
        self.assertEqual(sane_repr('short', 1024), "'short'")
        self.assertEqual(sane_repr(u'short', 1024), "u'short'")
        self.assertEqual(sane_repr(ValueError('A message'), 1024), "ValueError('A message',)")

        self.assertEqual(sane_repr('something longer', 10), "'something [truncated]...")

        self.assertEqual(sane_repr('ěščřž', 1024), "'\\xc4\\x9b\\xc5\\xa1\\xc4\\x8d\\xc5\\x99\\xc5\\xbe'")
        self.assertEqual(sane_repr(u'ěščřž', 1024), "u'\\u011b\\u0161\\u010d\\u0159\\u017e'")


class SentinelRecoder(CorbaRecoder):
    """
    Corba recoder for tests. Keeps sentinels untouched.
    """
    def __init__(self, coding='utf-8'):
        super(SentinelRecoder, self).__init__(coding)
        self.add_recode_function(type(sentinel.DEFAULT), self._identity, self._identity)


class InternalServerError(CORBA.UserException):
    """
    Internal server error for tests.
    """


class CustomError(CORBA.UserException):
    """
    Custom CORBA exception for tests.
    """


class TestCorbaClient(unittest.TestCase):
    """
    Tests for `CorbaClient` class.
    """
    def setUp(self):
        self.corba_object = Mock(spec=['method'])
        # Set the default result
        self.corba_object.method.return_value = sentinel.result
        self.corba_client = CorbaClient(self.corba_object, SentinelRecoder(), InternalServerError)

        # Mock logging
        self.log_handler = BufferingHandler(10)
        logger = logging.getLogger('pyfco.client')
        patcher = patch.object(logger, 'handlers', [self.log_handler])
        self.addCleanup(patcher.stop)
        patcher.start()
        self.addCleanup(logger.setLevel, logger.level)
        logger.setLevel(logging.DEBUG)

    def assertLogs(self, levels, messages):
        """
        Verifies logs
        """
        # Match levels
        self.assertEqual([m.levelname for m in self.log_handler.buffer], levels)
        # Match messages
        for message, expected in zip(self.log_handler.buffer, messages):
            self.assertRegexpMatches(message.getMessage(), expected)

    def test_call(self):
        self.corba_client.method()
        self.assertEqual(self.corba_object.mock_calls, [call.method()])

        self.assertLogs(['DEBUG', 'DEBUG'], ('method()', 'method returned'))

    def test_call_args(self):
        self.corba_client.method(sentinel.arg, sentinel.other_arg)
        self.assertEqual(self.corba_object.mock_calls, [call.method(sentinel.arg, sentinel.other_arg)])

    def test_call_kwargs_forbidden(self):
        with self.assertRaises(TypeError):
            self.corba_client.method(key=sentinel.value, other_key=sentinel.other_value)

    def test_return_value(self):
        self.assertEqual(self.corba_client.method(), sentinel.result)
        self.assertEqual(self.corba_object.mock_calls, [call.method()])

    def test_args_encoded(self):
        # Test strings in arguments are encoded before corba is called
        self.corba_client.method(u'ěščřž', u'ýáíé')
        self.assertEqual(self.corba_object.mock_calls, [call.method('ěščřž', 'ýáíé')])
        self.assertIsInstance(self.corba_object.mock_calls[0][1][0], str)
        self.assertIsInstance(self.corba_object.mock_calls[0][1][1], str)

    def test_result_decoded(self):
        # Test strings in result are decoded
        self.corba_object.method.return_value = 'ěščřžýáíé'
        result = self.corba_client.method()
        self.assertEqual(result, u'ěščřžýáíé')
        self.assertIsInstance(result, unicode)

    def test_unknown_method(self):
        with self.assertRaises(AttributeError):
            self.corba_client.unknown()

        self.assertEqual(self.corba_object.mock_calls, [])

    def test_internal_server_error(self):
        self.corba_object.method.side_effect = InternalServerError
        with self.assertRaises(InternalServerError):
            self.corba_client.method()

        self.assertEqual(self.corba_object.mock_calls, [call.method()])
        self.assertLogs(['DEBUG', 'ERROR'], ('method()', 'method failed with .*InternalServerError'))

    def test_user_exception(self):
        self.corba_object.method.side_effect = CustomError
        with self.assertRaises(CustomError):
            self.corba_client.method()

        self.assertEqual(self.corba_object.mock_calls, [call.method()])
        self.assertLogs(['DEBUG', 'DEBUG'], ('method()', 'method failed with .*CustomError'))

    def test_corba_exception(self):
        self.corba_object.method.side_effect = CORBA.TRANSIENT
        with self.assertRaises(CORBA.TRANSIENT):
            self.corba_client.method()

        self.assertEqual(self.corba_object.mock_calls, [call.method()])
        self.assertLogs(['DEBUG', 'ERROR'], ('method()', 'method failed with CORBA.TRANSIENT'))


class TestCorbaClientProxy(unittest.TestCase):
    """
    Test `CorbaClientProxy` class.
    """
    def test_proxy(self):
        client_1 = Mock()
        client_2 = Mock()

        proxy = CorbaClientProxy(client_1)
        self.assertEqual(proxy.client, client_1)
        proxy.foo()
        proxy.client = client_2
        self.assertEqual(proxy.client, client_2)
        proxy.bar()

        self.assertEqual(client_1.mock_calls, [call.foo()])
        self.assertEqual(client_2.mock_calls, [call.bar()])
