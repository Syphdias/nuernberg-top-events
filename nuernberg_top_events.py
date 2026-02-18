#!/usr/bin/env python3
import re
from dataclasses import dataclass
from datetime import datetime

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


def parse_date_string(date_str: str, year: int = 2026) -> EventDate | None:
    """Parse German date string and return EventDate object."""
    date_str = date_str.strip()

    # Skip future events
    if "Erst wieder" in date_str:
        return None

    # Month only (e.g., "August")
    if date_str in MONTHS:
        month_num = MONTHS[date_str]
        last_day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month_num - 1]
        return EventDate(
            datetime(year, month_num, 1), datetime(year, month_num, last_day), date_str
        )

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
                return EventDate(
                    datetime(year, start_month, int(start_match.group(1))),
                    datetime(year, end_month, int(end_match.group(1))),
                )

    # Multiple dates (e.g., "15. und 16. Februar" or "26. Juli und 8. August")
    if "und" in date_str:
        parts = date_str.split("und")
        first_match = re.search(r"(\d+)\.\s*(\w+)?", parts[0])
        second_match = re.search(r"(\d+)\.\s*(\w+)", parts[1])
        if first_match and second_match:
            month2 = MONTHS.get(second_match.group(2))
            if month2:
                if first_match.group(2) and first_match.group(2) in MONTHS:
                    # Different months - return as separate dates (stored in start only)
                    month1 = MONTHS[first_match.group(2)]
                    return EventDate(
                        datetime(year, month1, int(first_match.group(1))),
                        datetime(year, month2, int(second_match.group(1))),
                    )
                # Same month - return as range
                return EventDate(
                    datetime(year, month2, int(first_match.group(1))),
                    datetime(year, month2, int(second_match.group(1))),
                )

    # Single date (e.g., "9. August" or "Ab 1. Mai")
    match = re.search(r"(\d+)\.\s*(\w+)", date_str)
    if match:
        month = MONTHS.get(match.group(2))
        if month:
            return EventDate(datetime(year, month, int(match.group(1))))

    return None


def format_event(title: str, event_date: EventDate) -> str:
    """Format event for output."""
    if event_date.month_name:
        title_with_month = f"{title} ({event_date.month_name})"
    else:
        title_with_month = title

    if event_date.end:
        # Check if it's "X. Juli und Y. August" format (different months with small gap)
        days_diff = (event_date.end - event_date.start).days
        is_separate_dates = (
            event_date.start.month != event_date.end.month
            and days_diff <= 14
            and event_date.start.day > 20
        )
        if is_separate_dates:
            start_str = event_date.start.strftime("%Y-%m-%d")
            end_str = event_date.end.strftime("%Y-%m-%d")
            return f"{title_with_month}: {start_str}, {end_str}"
        else:
            start_str = event_date.start.strftime("%Y-%m-%d")
            end_str = event_date.end.strftime("%Y-%m-%d")
            return f"{title_with_month}: {start_str} - {end_str}"
    else:
        return f"{title_with_month}: {event_date.start.strftime('%Y-%m-%d')}"


def fetch_events_for_year(year: int):
    """Fetch events from the Nürnberg website for a specific year."""
    import urllib.request

    url = "https://www.nuernberg.de/internet/stadtportal/veranstaltungen_events_highlights.html"
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode("utf-8")

        # Check if this page is for the requested year
        year_match = re.search(r"Top-Events (\d{4})", html)
        page_year = int(year_match.group(1)) if year_match else None

        if page_year != year:
            return []  # Page doesn't have events for this year

        headers = re.findall(r"<h2[^>]*>([^<]+)</h2>", html)
        events = []

        for header in headers:
            if ":" not in header:
                continue

            date_str, title = header.split(":", 1)
            event_date = parse_date_string(date_str.strip(), year)

            if event_date:
                events.append((title.strip(), event_date))

        return events
    except Exception:
        return []


def main():
    import argparse
    import sys
    from datetime import datetime as dt

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

    current_year = dt.now().year

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
        from icalendar import Calendar, Event

        cal = Calendar()
        cal.add("prodid", "-//Nürnberg Top Events//nuernberg.de//")
        cal.add("version", "2.0")
        cal.add("x-wr-calname", "Nürnberg Top Events")
        cal.add("x-wr-caldesc", "Top events in Nürnberg")

        for title, event_date in all_events:
            event = Event()
            event.add("summary", title)
            event.add("dtstart", event_date.start.date())
            if event_date.end:
                event.add("dtend", event_date.end.date())
            else:
                event.add("dtend", event_date.start.date())
            cal.add_component(event)

        filename = "nuernberg_top_events.ical"
        with open(filename, "wb") as f:
            f.write(cal.to_ical())
        print(f"Generated {filename} with {len(all_events)} events")


if __name__ == "__main__":
    main()
