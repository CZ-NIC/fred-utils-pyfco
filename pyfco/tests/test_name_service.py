"""Test `pyfco.name_service` module."""
import unittest

import CosNaming
from mock import Mock, call, patch, sentinel
from testfixtures import ShouldWarn

from pyfco.name_service import CorbaNameServiceClient, init_omniorb_exception_handles


class TestInitOmniorbExceptionHandles(unittest.TestCase):
    """Test `init_omniorb_exception_handles`."""

    def test_init_omniorb_exception_handles(self):
        msg = "'init_omniorb_exception_handles' is obsolete and does nothing. It should be removed."
        with ShouldWarn(DeprecationWarning(msg)):
            init_omniorb_exception_handles(sentinel)


class TestCorbaNameServiceClient(unittest.TestCase):
    """Test `CorbaNameServiceClient` class."""

    def test_retry_handler(self):
        client = CorbaNameServiceClient(sentinel.orb, retries=3)

        self.assertTrue(client.retry_handler(sentinel.cookie, 0, sentinel.exc))
        self.assertTrue(client.retry_handler(sentinel.cookie, 1, sentinel.exc))
        self.assertTrue(client.retry_handler(sentinel.cookie, 2, sentinel.exc))
        self.assertFalse(client.retry_handler(sentinel.cookie, 3, sentinel.exc))
        self.assertFalse(client.retry_handler(sentinel.cookie, 17, sentinel.exc))

    def test_corba_connect(self):
        mock_orb = Mock()
        mock_obj = mock_orb.string_to_object.return_value
        mock_obj._narrow.return_value = sentinel.context
        corba_obj = CorbaNameServiceClient(mock_orb)

        with patch('pyfco.name_service.installTransientExceptionHandler', autospec=True) as install_mock:
            corba_obj.connect()

        self.assertEqual(corba_obj.context, sentinel.context)
        self.assertEqual(mock_orb.mock_calls, [
            call.string_to_object('corbaname::localhost'),
            call.string_to_object()._narrow(CosNaming.NamingContext),
        ])
        self.assertEqual(install_mock.mock_calls, [call(None, corba_obj.retry_handler, mock_obj)])

    def test_corba_get_object(self):
        mock_orb = Mock()
        with patch('pyfco.name_service.installTransientExceptionHandler', autospec=True):
            with patch.object(CosNaming, "NameComponent") as mock_name_component:
                corba_obj = CorbaNameServiceClient(mock_orb)
                corba_obj.get_object("Logger", "ccRegTest.Logger")
        self.assertEqual(mock_name_component.mock_calls, [
            call('fred', 'context'),
            call('Logger', 'Object'),
        ])
        self.assertEqual(mock_orb.mock_calls, [
            call.string_to_object('corbaname::localhost'),
            call.string_to_object()._narrow(CosNaming.NamingContext),
            call.string_to_object()._narrow().resolve([mock_name_component(), mock_name_component()]),
            call.string_to_object()._narrow().resolve()._narrow('ccRegTest.Logger')
        ])

    def test_corba_context_is_not_none(self):
        mock_orb = Mock()
        mock_context = Mock()
        with patch('pyfco.name_service.installTransientExceptionHandler', autospec=True):
            with patch.object(CosNaming, "NameComponent") as mock_name_component:
                corba_obj = CorbaNameServiceClient(mock_orb)
                corba_obj.context = mock_context
                corba_obj.get_object("Logger", "ccRegTest.Logger")
        self.assertEqual(mock_context.mock_calls, [
            call.resolve([mock_name_component.return_value, mock_name_component.return_value]),
            call.resolve()._narrow('ccRegTest.Logger')
        ])
        self.assertEqual(mock_name_component.mock_calls, [
            call('fred', 'context'),
            call('Logger', 'Object')
        ])
        self.assertEqual(mock_orb.mock_calls, [])
