#!/usr/bin/env python3
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

MONTHS = {
    "Januar": 1,
    "Februar": 2,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12,
}


@dataclass
class EventDate:
    start: datetime
    end: datetime | None = None
    month_name: str | None = None
    starts_with_ab: bool = False


def parse_date_string(date_str: str, year: int | None = None) -> list[EventDate]:
    """Parse German date string and return list of EventDate objects.

    Args:
        date_str: German date string (e.g., "9. August", "24. April 2027", "August")
        year: Year to use if not specified in date string. If None, uses current year.

    Returns:
        List of EventDate objects.
    """
    from datetime import datetime as dt

    # Use current year if not provided
    if year is None:
        year = dt.now().year

    date_str = date_str.strip().rstrip(":")

    # Skip future events (only skip "Erst wieder" text without dates)
    if date_str == "Erst wieder" or date_str.startswith("Erst wieder "):
        return []

    # Explicit year in date (e.g., "24. April 2027" or "Herbst 2027") - use the year from the date
    explicit_year: int | None = None
    year_match = re.search(r"(\d{4})$", date_str.strip())
    if year_match:
        explicit_year = int(year_match.group(1))
        date_str = re.sub(r"\s+\d{4}$", "", date_str).strip()
        # If nothing left after extracting year, skip
        if not date_str:
            return []
        # Use extracted year instead of parameter
        year = explicit_year

    # Month only (e.g., "August")
    if date_str in MONTHS:
        month_num = MONTHS[date_str]
        last_day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month_num - 1]
        return [
            EventDate(datetime(year, month_num, 1), datetime(year, month_num, last_day), date_str)
        ]

    # Date range (e.g., "4. bis 8. März" or "27. Februar bis 8. März")
    if "bis" in date_str:
        parts = date_str.split("bis")
        start_match = re.search(r"(\d+)\.\s*(\w+)?", parts[0])
        end_match = re.search(r"(\d+)\.\s*(\w+)", parts[1])
        if start_match and end_match:
            end_month = MONTHS.get(end_match.group(2))
            if end_month:
                start_month = (
                    MONTHS.get(start_match.group(2)) if start_match.group(2) else end_month
                )
                return [
                    EventDate(
                        datetime(year, start_month, int(start_match.group(1))),
                        datetime(year, end_month, int(end_match.group(1))),
                    )
                ]

    # Multiple dates (e.g., "15. und 16. Februar" or "26. Juli und 8. August")
    if "und" in date_str:
        parts = date_str.split("und")
        first_match = re.search(r"(\d+)\.\s*(\w+)?", parts[0])
        second_match = re.search(r"(\d+)\.\s*(\w+)", parts[1])
        if first_match and second_match:
            month2 = MONTHS.get(second_match.group(2))
            if month2:
                if first_match.group(2) and first_match.group(2) in MONTHS:
                    # Different months - return as two separate dates
                    month1 = MONTHS[first_match.group(2)]
                    return [
                        EventDate(datetime(year, month1, int(first_match.group(1)))),
                        EventDate(datetime(year, month2, int(second_match.group(1)))),
                    ]
                # Same month - return as range
                return [
                    EventDate(
                        datetime(year, month2, int(first_match.group(1))),
                        datetime(year, month2, int(second_match.group(1))),
                    )
                ]

    # Single date (e.g., "9. August" or "Ab 1. Mai")
    match = re.search(r"(\d+)\.\s*(\w+)", date_str)
    if match:
        month = MONTHS.get(match.group(2))
        if month:
            starts_with_ab = date_str.strip().lower().startswith("ab")
            return [
                EventDate(datetime(year, month, int(match.group(1))), starts_with_ab=starts_with_ab)
            ]

    return []


def format_event(title: str, event_date: EventDate) -> str:
    """Format event for output."""
    if event_date.month_name:
        title_with_month = f"{title} ({event_date.month_name})"
    else:
        title_with_month = title

    date_suffix = " (ab heute)" if event_date.starts_with_ab else ""

    if event_date.end:
        start_str = event_date.start.strftime("%Y-%m-%d")
        end_str = event_date.end.strftime("%Y-%m-%d")
        return f"{title_with_month}: {start_str} - {end_str}{date_suffix}"
    else:
        return f"{title_with_month}: {event_date.start.strftime('%Y-%m-%d')}{date_suffix}"


def fetch_events_for_year(year: int):
    """Fetch events from the Nürnberg website for a specific year."""
    import urllib.request

    url = "https://www.nuernberg.de/internet/stadtportal/veranstaltungen_events_highlights.html"
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode("utf-8")

        year_match = re.search(r"Top-Events (\d{4})", html)
        if year_match:
            page_year = int(year_match.group(1))
            if page_year != year:
                return []

        heading_spans = re.findall(
            r'class="link--tile__heading"[^>]*>([^<]+?)(?:<br>|:\s*)([^<]+)</span>', html
        )
        events = []

        for date_str, title in heading_spans:
            event_dates = parse_date_string(date_str.strip(), year)

            for event_date in event_dates:
                events.append((title.strip(), event_date))

        return events
    except Exception:
        return []


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Parse Nürnberg events")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print parsed events without generating iCal file",
    )
    parser.add_argument("--ical", action="store_true", help="Generate iCal file")
    parser.add_argument(
        "--min-events",
        type=int,
        default=10,
        help="Minimum number of events required (default: 10)",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.ical:
        args.dry_run = True

    current_year = datetime.now().year

    # Fetch events for current and next year
    all_events = []
    for year in [current_year, current_year + 1]:
        events = fetch_events_for_year(year)
        all_events.extend(events)

    # Safety check: ensure we have a reasonable number of events
    if len(all_events) < args.min_events:
        print(
            f"ERROR: Only found {len(all_events)} events (minimum: {args.min_events})",
            file=sys.stderr,
        )
        print(
            "Website may be unavailable or format changed. Not updating calendar.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.dry_run:
        for title, event_date in all_events:
            print(format_event(title, event_date))

    if args.ical:
        cal = generate_ical_from_events(all_events)
        filename = "nuernberg_top_events.ical"
        with open(filename, "wb") as f:
            f.write(cal.to_ical())
        print(f"Generated {filename} with {len(all_events)} events")


def generate_ical_from_events(events: list[tuple[str, EventDate]]):
    """Generate iCal calendar from events list.

    Args:
        events: List of tuples containing (title, EventDate)

    Returns:
        iCal Calendar object
    """
    from icalendar import Calendar, Event

    cal = Calendar()
    cal.add("prodid", "-//Nürnberg Top Events//nuernberg.de//")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", "Nürnberg Top Events")
    cal.add("x-wr-caldesc", "Top Events in Nürnberg")

    for title, event_date in events:
        event = Event()
        event.add("summary", title)
        event.add("dtstart", event_date.start.date())
        if event_date.end:
            event.add("dtend", (event_date.end + timedelta(days=1)).date())
        else:
            event.add("dtend", (event_date.start + timedelta(days=1)).date())
        cal.add_component(event)

    return cal


if __name__ == "__main__":
    main()
