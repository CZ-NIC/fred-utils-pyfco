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

    def test_corba_orb_deprecated(self):
        with ShouldWarn(DeprecationWarning("'orb' argument is deprecated and should be removed.")):
            CorbaNameServiceClient(orb=sentinel.orb)

    def test_corba_connect(self):
        corba_obj = CorbaNameServiceClient()

        with patch('pyfco.name_service.installTransientExceptionHandler', autospec=True) as install_mock:
            with patch('pyfco.name_service.CORBA.ORB_init', autospec=True) as init_mock:
                init_mock.return_value.string_to_object.return_value._narrow.return_value = sentinel.context
                corba_obj.connect()

        self.assertEqual(corba_obj.context, sentinel.context)
        calls = [call(['-ORBnativeCharCodeSet', 'UTF-8']),
                 call().string_to_object('corbaname::localhost'),
                 call().string_to_object()._narrow(CosNaming.NamingContext)]
        self.assertEqual(init_mock.mock_calls, calls)
        self.assertEqual(install_mock.mock_calls,
                         [call(None, corba_obj.retry_handler, init_mock.return_value.string_to_object.return_value)])

    def test_corba_get_object(self):
        corba_obj = CorbaNameServiceClient()
        with patch('pyfco.name_service.installTransientExceptionHandler', autospec=True):
            with patch('pyfco.name_service.CORBA.ORB_init', autospec=True) as init_mock:
                with patch.object(CosNaming, "NameComponent") as mock_name_component:
                    corba_obj.get_object("Logger", "ccRegTest.Logger")
        self.assertEqual(mock_name_component.mock_calls, [
            call('fred', 'context'),
            call('Logger', 'Object'),
        ])
        calls = [call(['-ORBnativeCharCodeSet', 'UTF-8']),
                 call().string_to_object('corbaname::localhost'),
                 call().string_to_object()._narrow(CosNaming.NamingContext),
                 call().string_to_object()._narrow().resolve([mock_name_component(), mock_name_component()]),
                 call().string_to_object()._narrow().resolve()._narrow('ccRegTest.Logger')]
        self.assertEqual(init_mock.mock_calls, calls)

    def test_corba_context_is_not_none(self):
        mock_context = Mock()
        corba_obj = CorbaNameServiceClient()
        corba_obj.context = mock_context

        with patch('pyfco.name_service.installTransientExceptionHandler', autospec=True):
            with patch.object(CosNaming, "NameComponent") as mock_name_component:
                corba_obj.get_object("Logger", "ccRegTest.Logger")
        self.assertEqual(mock_context.mock_calls, [
            call.resolve([mock_name_component.return_value, mock_name_component.return_value]),
            call.resolve()._narrow('ccRegTest.Logger')
        ])
        self.assertEqual(mock_name_component.mock_calls, [
            call('fred', 'context'),
            call('Logger', 'Object')
        ])
