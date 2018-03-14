"""Utilities."""
from __future__ import unicode_literals

import inspect
from unittest.util import safe_repr

import omniORB
import six


class CorbaAssertMixin(object):
    """Mixin for `TestCase` which provides methods to compare corba objects."""

    corba_equality_funcs = {}

    def _getAssertEqualityFunc(self, first, second):
        if isinstance(first, omniORB.StructBase):
            return self._get_corba_equality_func(first)
        return super(CorbaAssertMixin, self)._getAssertEqualityFunc(first, second)

    def _get_corba_equality_func(self, first):
        asserter = self.corba_equality_funcs.get(first.__class__)
        if asserter is not None:
            if isinstance(asserter, six.string_types):
                asserter = getattr(self, asserter)
            return asserter
        return self._base_struct_equal

    def _base_struct_equal(self, first, second, msg=None):
        """Compare corba structures."""
        self.assertIsInstance(first, omniORB.StructBase, "First argument is not a corba structure")
        self.assertIsInstance(second, omniORB.StructBase, "Second argument is not a corba structure")

        standard_msg = "%s != %s" % (safe_repr(first), safe_repr(second))
        msg = self._formatMessage(msg, standard_msg)

        self.assertEqual(first.__class__, second.__class__, msg)

        args = inspect.getargspec(first.__class__.__init__).args
        self.assertEqual(args[0], 'self',
                         "First argument of the '%s.__init__' is not 'self'" % first.__class__.__name__)
        args = args[1:]
        self.assertTrue(args, "Structure '%s' has no attributes" % first.__class__.__name__)

        for arg in args:
            self.assertEqual(getattr(first, arg), getattr(second, arg), msg)

    def assertCorbaCallsEqual(self, real_calls, expected_calls, msg=None):
        """Compare two lists of calls comparing corba objects."""
        standard_msg = "%s != %s" % (safe_repr(real_calls), safe_repr(expected_calls))
        msg = self._formatMessage(msg, standard_msg)
        self.assertEqual(len(real_calls), len(expected_calls), msg)

        for real, expected in zip(real_calls, expected_calls):
            real_name, real_args, real_kwargs = real
            exp_name, exp_args, exp_kwargs = expected

            self.assertEqual(real_name, exp_name, msg)

            # Check arguments
            self.assertEqual(len(real_args), len(exp_args), msg)
            for real_arg, exp_arg in zip(real_args, exp_args):
                # We already taught assertEqual how to compare corba objects.
                self.assertEqual(real_arg, exp_arg, msg)

            # Check keyword arguments
            self.assertEqual(real_kwargs.keys(), exp_kwargs.keys(), msg)
            for key in real_kwargs:
                # We already taught assertEqual how to compare corba objects.
                self.assertEqual(real_kwargs[key], exp_kwargs[key], msg)
