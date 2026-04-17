#!/usr/bin/env python3
import unittest
from datetime import datetime

from nuernberg_top_events import parse_date_string


class TestDateParsing(unittest.TestCase):
    def test_single_date_returns_list(self):
        result = parse_date_string("9. August")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, datetime(2026, 8, 9))
        self.assertIsNone(result[0].end)

    def test_month_only_returns_list(self):
        result = parse_date_string("August")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, datetime(2026, 8, 1))
        self.assertEqual(result[0].end, datetime(2026, 8, 31))
        self.assertEqual(result[0].month_name, "August")

    def test_bis_returns_list_with_one_event(self):
        result = parse_date_string("28. bis 30. August")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, datetime(2026, 8, 28))
        self.assertEqual(result[0].end, datetime(2026, 8, 30))

    def test_bis_different_months_returns_one_event(self):
        result = parse_date_string("15. September bis 10. Oktober")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, datetime(2026, 9, 15))
        self.assertEqual(result[0].end, datetime(2026, 10, 10))

    def test_bis_implicit_start_month(self):
        result = parse_date_string("4. bis 8. März")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, datetime(2026, 3, 4))
        self.assertEqual(result[0].end, datetime(2026, 3, 8))

    def test_und_same_month_returns_one_event(self):
        result = parse_date_string("1. und 2. August")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, datetime(2026, 8, 1))
        self.assertEqual(result[0].end, datetime(2026, 8, 2))

    def test_und_different_months_returns_two_events(self):
        result = parse_date_string("26. Juli und 8. August")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].start, datetime(2026, 7, 26))
        self.assertIsNone(result[0].end)
        self.assertEqual(result[1].start, datetime(2026, 8, 8))
        self.assertIsNone(result[1].end)

    def test_future_event_returns_empty_list(self):
        result = parse_date_string("Erst wieder 2027")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_date_with_prefix_returns_list(self):
        result = parse_date_string("Ab 3. August")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].start, datetime(2026, 8, 3))
        self.assertIsNone(result[0].end)
        self.assertTrue(result[0].starts_with_ab)

    def test_date_without_ab_prefix(self):
        result = parse_date_string("9. August")
        self.assertFalse(result[0].starts_with_ab)


class TestICalGeneration(unittest.TestCase):
    def test_dtend_is_exclusive_with_bis(self):
        event_dates = parse_date_string("28. bis 30. August")
        events = [("Test Event", ed) for ed in event_dates]
        from nuernberg_top_events import generate_ical_from_events

        cal = generate_ical_from_events(events)
        self.assertEqual(len(list(cal.walk("VEVENT"))), 1)
        event = list(cal.walk("VEVENT"))[0]
        self.assertEqual(event["DTSTART"].dt, datetime(2026, 8, 28).date())
        self.assertEqual(event["DTEND"].dt, datetime(2026, 8, 31).date())

    def test_und_different_months_creates_two_events(self):
        event_dates = parse_date_string("26. Juli und 8. August")
        events = [("Test Event", ed) for ed in event_dates]
        from nuernberg_top_events import generate_ical_from_events

        cal = generate_ical_from_events(events)
        self.assertEqual(len(list(cal.walk("VEVENT"))), 2)
        vevents = list(cal.walk("VEVENT"))
        self.assertEqual(vevents[0]["DTSTART"].dt, datetime(2026, 7, 26).date())
        self.assertEqual(vevents[0]["DTEND"].dt, datetime(2026, 7, 27).date())
        self.assertEqual(vevents[1]["DTSTART"].dt, datetime(2026, 8, 8).date())
        self.assertEqual(vevents[1]["DTEND"].dt, datetime(2026, 8, 9).date())

    def test_dtend_single_date(self):
        event_dates = parse_date_string("9. August")
        events = [("Test Event", ed) for ed in event_dates]
        from nuernberg_top_events import generate_ical_from_events

        cal = generate_ical_from_events(events)
        event = list(cal.walk("VEVENT"))[0]
        self.assertEqual(event["DTSTART"].dt, datetime(2026, 8, 9).date())
        self.assertEqual(event["DTEND"].dt, datetime(2026, 8, 10).date())

    def test_dtend_month_only(self):
        event_dates = parse_date_string("August")
        events = [("Test Event", ed) for ed in event_dates]
        from nuernberg_top_events import generate_ical_from_events

        cal = generate_ical_from_events(events)
        event = list(cal.walk("VEVENT"))[0]
        self.assertEqual(event["DTSTART"].dt, datetime(2026, 8, 1).date())
        self.assertEqual(event["DTEND"].dt, datetime(2026, 9, 1).date())


class TestEventFormatting(unittest.TestCase):
    def test_format_range_with_bis(self):
        from nuernberg_top_events import format_event

        event_dates = parse_date_string("22. Juni bis 2. Juli")
        result = format_event("Digital Festival", event_dates[0])
        self.assertIn(" - ", result)
        self.assertNotIn(",", result)

    def test_format_separate_date_single(self):
        from nuernberg_top_events import format_event

        event_dates = parse_date_string("26. Juli und 8. August")
        result = format_event("Klassik Open Air", event_dates[0])
        self.assertNotIn(" - ", result)
        result2 = format_event("Klassik Open Air", event_dates[1])
        self.assertNotIn(" - ", result2)


if __name__ == "__main__":
    unittest.main()
