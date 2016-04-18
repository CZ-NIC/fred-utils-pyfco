import sys
import unittest

import CosNaming
from mock import Mock, call, patch, sentinel

from pyfco import corba


class TestCorba(unittest.TestCase):

    def setUp(self):
        sys.modules["ccRegTest"] = Mock()

    def tearDown(self):
        del sys.modules["ccRegTest"]

    def test_transient_failure(self):
        self.assertTrue(corba.transient_failure(None, 0, None))
        self.assertTrue(corba.transient_failure(None, 10, None))
        self.assertFalse(corba.transient_failure(None, 11, None))
        self.assertFalse(corba.transient_failure(None, 21, None))

    def test_comm_failure(self):
        self.assertTrue(corba.comm_failure(None, 0, None))
        self.assertTrue(corba.comm_failure(None, 20, None))
        self.assertFalse(corba.comm_failure(None, 21, None))
        self.assertFalse(corba.comm_failure(None, 31, None))

    def test_system_failure(self):
        self.assertTrue(corba.system_failure(None, 0, None))
        self.assertTrue(corba.system_failure(None, 5, None))
        self.assertFalse(corba.system_failure(None, 6, None))
        self.assertFalse(corba.system_failure(None, 16, None))

    @patch("pyfco.corba.omniORB")
    def test_init_omniorb_exception_handles(self, mock_omniorb):
        corba.init_omniorb_exception_handles(sentinel)
        self.assertEqual(mock_omniorb.mock_calls, [
            call.installTransientExceptionHandler(sentinel, corba.transient_failure),
            call.installCommFailureExceptionHandler(sentinel, corba.comm_failure),
            call.installSystemExceptionHandler(sentinel, corba.system_failure)
        ])

    def test_corba_init_default(self):
        corba_obj = corba.CorbaNameServiceClient(sentinel.orb)
        self.assertEqual(corba_obj.host_port, "localhost")
        self.assertEqual(corba_obj.context_name, "fred")
        self.assertEqual(corba_obj.__dict__.keys(), ['host_port', 'orb', 'context', 'context_name'])

    def test_corba_connect(self):
        mock_orb = Mock()
        corba_obj = corba.CorbaNameServiceClient(mock_orb)
        corba_obj.connect()
        self.assertEqual(mock_orb.mock_calls, [
            call.string_to_object('corbaname::localhost'),
            call.string_to_object()._narrow(CosNaming.NamingContext),
        ])

    def test_corba_get_object(self):
        mock_orb = Mock()
        with patch.object(CosNaming, "NameComponent") as mock_name_component:
            corba_obj = corba.CorbaNameServiceClient(mock_orb)
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
        with patch.object(CosNaming, "NameComponent") as mock_name_component:
            corba_obj = corba.CorbaNameServiceClient(mock_orb)
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
