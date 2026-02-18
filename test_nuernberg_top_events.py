#!/usr/bin/env python3
import unittest
from datetime import datetime

from nuernberg_top_events import parse_date_string


class TestDateParsing(unittest.TestCase):

    def test_single_date(self):
        result = parse_date_string("9. August")
        self.assertEqual(result.start, datetime(2026, 8, 9))
        self.assertIsNone(result.end)

    def test_month_only(self):
        result = parse_date_string("August")
        self.assertEqual(result.start, datetime(2026, 8, 1))
        self.assertEqual(result.end, datetime(2026, 8, 31))
        self.assertEqual(result.month_name, "August")

    def test_date_range_same_month(self):
        result = parse_date_string("28. bis 30. August")
        self.assertEqual(result.start, datetime(2026, 8, 28))
        self.assertEqual(result.end, datetime(2026, 8, 30))

    def test_date_range_different_months(self):
        result = parse_date_string("15. September bis 10. Oktober")
        self.assertEqual(result.start, datetime(2026, 9, 15))
        self.assertEqual(result.end, datetime(2026, 10, 10))

    def test_date_range_implicit_start_month(self):
        result = parse_date_string("4. bis 8. März")
        self.assertEqual(result.start, datetime(2026, 3, 4))
        self.assertEqual(result.end, datetime(2026, 3, 8))

    def test_multiple_dates_same_month(self):
        result = parse_date_string("1. und 2. August")
        self.assertEqual(result.start, datetime(2026, 8, 1))
        self.assertEqual(result.end, datetime(2026, 8, 2))

    def test_multiple_dates_different_months(self):
        result = parse_date_string("26. Juli und 8. August")
        self.assertEqual(result.start, datetime(2026, 7, 26))
        self.assertEqual(result.end, datetime(2026, 8, 8))

    def test_future_event(self):
        result = parse_date_string("Erst wieder 2027")
        self.assertIsNone(result)

    def test_date_with_prefix(self):
        result = parse_date_string("Ab 3. August")
        self.assertEqual(result.start, datetime(2026, 8, 3))
        self.assertIsNone(result.end)


if __name__ == "__main__":
    unittest.main()
