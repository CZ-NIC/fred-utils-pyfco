#
# Copyright (C) 2016-2018  CZ.NIC, z. s. p. o.
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

"""Test `pyfco.name_service` module."""
from __future__ import unicode_literals

import unittest

import CosNaming
import six
from mock import Mock, call, patch, sentinel
from testfixtures import ShouldWarn

from pyfco.name_service import CorbaNameServiceClient


class TestCorbaNameServiceClient(unittest.TestCase):
    """Test `CorbaNameServiceClient` class."""

    def test_retry_handler(self):
        client = CorbaNameServiceClient(sentinel.orb, retries=3)

        self.assertTrue(client.retry_handler(sentinel.cookie, 0, sentinel.exc))
        self.assertTrue(client.retry_handler(sentinel.cookie, 1, sentinel.exc))
        self.assertTrue(client.retry_handler(sentinel.cookie, 2, sentinel.exc))
        self.assertFalse(client.retry_handler(sentinel.cookie, 3, sentinel.exc))
        self.assertFalse(client.retry_handler(sentinel.cookie, 17, sentinel.exc))

    def test_init(self):
        corba_obj = CorbaNameServiceClient(context_name='test')
        self.assertIsInstance(corba_obj.context_name, six.text_type)

    def test_init_bytes(self):
        with ShouldWarn(DeprecationWarning("Passing 'context_name' as six.binary_type is deprecated. "
                                           "Please pass six.text_type.")):
            corba_obj = CorbaNameServiceClient(context_name=b'test')
        self.assertIsInstance(corba_obj.context_name, six.text_type)

    def test_init_host_port(self):
        corba_obj = CorbaNameServiceClient(host_port='test')
        self.assertIsInstance(corba_obj.host_port, six.text_type)

    def test_init_host_port_bytes(self):
        with ShouldWarn(DeprecationWarning("Passing 'host_port' as six.binary_type is deprecated. "
                                           "Please pass six.text_type.")):
            corba_obj = CorbaNameServiceClient(host_port=b'test')
        self.assertIsInstance(corba_obj.host_port, six.text_type)

    def test_corba_connect(self):
        corba_obj = CorbaNameServiceClient()

        with patch('pyfco.name_service.installTransientExceptionHandler', autospec=True) as install_mock:
            with patch('pyfco.name_service.CORBA.ORB_init', autospec=True) as init_mock:
                init_mock.return_value.string_to_object.return_value._narrow.return_value = sentinel.context
                corba_obj.connect()

        self.assertEqual(corba_obj.context, sentinel.context)
        if six.PY2:
            calls = [call(['-ORBnativeCharCodeSet'.encode(), 'UTF-8'.encode()])]
        else:
            calls = [call(['-ORBnativeCharCodeSet', 'UTF-8'])]
        calls.extend([call().string_to_object('corbaname::localhost'),
                      call().string_to_object()._narrow(CosNaming.NamingContext)])
        self.assertEqual(init_mock.mock_calls, calls)
        self.assertEqual(install_mock.mock_calls,
                         [call(None, corba_obj.retry_handler, init_mock.return_value.string_to_object.return_value)])

    def test_corba_connect_bytes(self):
        class BytesCorbaNameServiceClient(CorbaNameServiceClient):
            """Client with orb_args as bytes."""

            orb_args = [b'-ORBnativeCharCodeSet', b'UTF-8']

        corba_obj = BytesCorbaNameServiceClient()

        with patch('pyfco.name_service.installTransientExceptionHandler', autospec=True) as install_mock:
            with patch('pyfco.name_service.CORBA.ORB_init', autospec=True) as init_mock:
                init_mock.return_value.string_to_object.return_value._narrow.return_value = sentinel.context
                corba_obj.connect()

        self.assertEqual(corba_obj.context, sentinel.context)
        if six.PY2:
            calls = [call(['-ORBnativeCharCodeSet'.encode(), 'UTF-8'.encode()])]
        else:
            calls = [call(['-ORBnativeCharCodeSet', 'UTF-8'])]
        calls.extend([call().string_to_object('corbaname::localhost'),
                      call().string_to_object()._narrow(CosNaming.NamingContext)])
        self.assertEqual(init_mock.mock_calls, calls)
        self.assertEqual(install_mock.mock_calls,
                         [call(None, corba_obj.retry_handler, init_mock.return_value.string_to_object.return_value)])

    def test_corba_get_object(self):
        corba_obj = CorbaNameServiceClient()
        with patch('pyfco.name_service.installTransientExceptionHandler', autospec=True):
            with patch('pyfco.name_service.CORBA.ORB_init', autospec=True) as init_mock:
                with patch.object(CosNaming, "NameComponent") as mock_name_component:
                    corba_obj.get_object("Logger", "ccRegTest.Logger")
        if six.PY2:
            name_calls = [call('fred'.encode(), 'context'.encode()),
                          call('Logger'.encode(), 'Object'.encode())]
            init_calls = [call(['-ORBnativeCharCodeSet'.encode(), 'UTF-8'.encode()])]
        else:
            name_calls = [call('fred', 'context'),
                          call('Logger', 'Object')]
            init_calls = [call(['-ORBnativeCharCodeSet', 'UTF-8'])]
        self.assertEqual(mock_name_component.mock_calls, name_calls)
        init_calls.extend([call().string_to_object('corbaname::localhost'),
                           call().string_to_object()._narrow(CosNaming.NamingContext),
                           call().string_to_object()._narrow().resolve([mock_name_component(), mock_name_component()]),
                           call().string_to_object()._narrow().resolve()._narrow('ccRegTest.Logger')])
        self.assertEqual(init_mock.mock_calls, init_calls)

    def test_corba_get_object_text(self):
        corba_obj = CorbaNameServiceClient()
        with patch('pyfco.name_service.installTransientExceptionHandler', autospec=True), \
                patch('pyfco.name_service.CORBA.ORB_init', autospec=True) as init_mock, \
                patch.object(CosNaming, "NameComponent") as mock_name_component, \
                ShouldWarn(DeprecationWarning("Passing 'name' as six.binary_type is deprecated. "
                                              "Please pass six.text_type.")):
            corba_obj.get_object(b"Logger", "ccRegTest.Logger")
        if six.PY2:
            name_calls = [call('fred'.encode(), 'context'.encode()),
                          call('Logger'.encode(), 'Object'.encode())]
            init_calls = [call(['-ORBnativeCharCodeSet'.encode(), 'UTF-8'.encode()])]
        else:
            name_calls = [call('fred', 'context'),
                          call('Logger', 'Object')]
            init_calls = [call(['-ORBnativeCharCodeSet', 'UTF-8'])]
        self.assertEqual(mock_name_component.mock_calls, name_calls)
        init_calls.extend([call().string_to_object('corbaname::localhost'),
                           call().string_to_object()._narrow(CosNaming.NamingContext),
                           call().string_to_object()._narrow().resolve([mock_name_component(), mock_name_component()]),
                           call().string_to_object()._narrow().resolve()._narrow('ccRegTest.Logger')])
        self.assertEqual(init_mock.mock_calls, init_calls)

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
        if six.PY2:
            self.assertEqual(mock_name_component.mock_calls, [
                call('fred'.encode(), 'context'.encode()),
                call('Logger'.encode(), 'Object'.encode())
            ])
        else:
            self.assertEqual(mock_name_component.mock_calls, [
                call('fred', 'context'),
                call('Logger', 'Object')
            ])
