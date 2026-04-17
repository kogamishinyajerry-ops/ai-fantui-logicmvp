"""Tests for NaN/Infinity clamping in _optional_request_float and _sample_times."""

import math
import unittest
from unittest import mock

from well_harness.demo_server import _optional_request_float
from well_harness.scenario_playback import _sample_times


class TestOptionalRequestFloatNaNInf(unittest.TestCase):
    def test_nan_returns_error(self):
        """sample_period_s=NaN should return error with invalid_numeric_value."""
        payload = {"sample_period_s": float("nan")}
        result, error = _optional_request_float(payload, "sample_period_s", default=0.5)
        self.assertEqual(result, 0.5)
        self.assertIsNotNone(error)
        self.assertEqual(error["error"], "invalid_numeric_value")
        self.assertEqual(error["field"], "sample_period_s")
        self.assertIn("finite", error["message"])

    def test_infinity_returns_error(self):
        """sample_period_s=Infinity should return error with invalid_numeric_value."""
        payload = {"sample_period_s": float("inf")}
        result, error = _optional_request_float(payload, "sample_period_s", default=0.5)
        self.assertEqual(result, 0.5)
        self.assertIsNotNone(error)
        self.assertEqual(error["error"], "invalid_numeric_value")
        self.assertEqual(error["field"], "sample_period_s")

    def test_negative_infinity_returns_error(self):
        """sample_period_s=-Infinity should return error with invalid_numeric_value."""
        payload = {"sample_period_s": float("-inf")}
        result, error = _optional_request_float(payload, "sample_period_s", default=0.5)
        self.assertEqual(result, 0.5)
        self.assertIsNotNone(error)
        self.assertEqual(error["error"], "invalid_numeric_value")
        self.assertEqual(error["field"], "sample_period_s")

    def test_zero_uses_default(self):
        """sample_period_s=0.0 should use default (caught by <= 0 check)."""
        payload = {"sample_period_s": 0.0}
        result, error = _optional_request_float(payload, "sample_period_s", default=0.5)
        self.assertEqual(result, 0.5)
        self.assertIsNotNone(error)
        self.assertEqual(error["error"], "invalid_workbench_request")
        self.assertIn("greater than zero", error["message"])

    def test_valid_positive_value_works(self):
        """sample_period_s=0.5 should work normally."""
        payload = {"sample_period_s": 0.5}
        result, error = _optional_request_float(payload, "sample_period_s", default=0.5)
        self.assertEqual(result, 0.5)
        self.assertIsNone(error)


class TestSampleTimesGuard(unittest.TestCase):
    def test_nan_raises_value_error(self):
        """_sample_times(10.0, NaN) should raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            _sample_times(10.0, float("nan"))
        self.assertIn("finite positive number", str(ctx.exception))

    def test_infinity_raises_value_error(self):
        """_sample_times(10.0, Infinity) should raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            _sample_times(10.0, float("inf"))
        self.assertIn("finite positive number", str(ctx.exception))

    def test_negative_infinity_raises_value_error(self):
        """_sample_times(10.0, -Infinity) should raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            _sample_times(10.0, float("-inf"))
        self.assertIn("finite positive number", str(ctx.exception))

    def test_zero_raises_value_error(self):
        """_sample_times(10.0, 0.0) should raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            _sample_times(10.0, 0.0)
        self.assertIn("finite positive number", str(ctx.exception))

    def test_negative_value_raises_value_error(self):
        """_sample_times(10.0, -1.0) should raise ValueError."""
        with self.assertRaises(ValueError) as ctx:
            _sample_times(10.0, -1.0)
        self.assertIn("finite positive number", str(ctx.exception))

    def test_valid_positive_period_works(self):
        """_sample_times(10.0, 0.5) should return valid tuple."""
        result = _sample_times(10.0, 0.5)
        self.assertIsInstance(result, tuple)
        self.assertGreater(len(result), 0)
        self.assertTrue(all(math.isfinite(v) for v in result))


if __name__ == "__main__":
    unittest.main()
