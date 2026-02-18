# Nürnberg Top Events Calendar

> **Disclaimer:** This project was entirely vibe coded with AI assistance. Use
> at your own risk!

Automatically generates calendar subscription from [top events in
Nürnberg](https://www.nuernberg.de/internet/stadtportal/veranstaltungen_events_highlights.html).

## Subscribe to Calendar

Add this URL to your calendar app:
<https://syphdias.github.io/nuernberg-top-events/nuernberg_top_events.ical>

### How to Subscribe

**Apple Calendar (iOS/macOS):**

1. Settings → Calendar → Accounts → Add Account → Other
2. Add Subscribed Calendar
3. Paste the URL above

**Google Calendar:**

1. Settings → Add calendar → From URL
2. Paste the URL above

**Outlook:**

1. Add calendar → Subscribe from web
2. Paste the URL above

## Development

**Run tests:**

```bash
uv run python test_nuernberg_top_events.py -v
```

**Generate calendar locally:**

```bash
uv run nuernberg-top-events --ical
```

**Dry run (print events):**

```bash
uv run nuernberg-top-events --dry-run
```

**Linting:**

```bash
uv run ruff check .
uv run black .
```

## License

I have no idea how licensing works with AI content, potentially public domain,
who knows. I included a MIT license in case it is relevant.
