# Nürnberg Top Events Calendar

> **Disclaimer (and slight rant):**
> This project was entirely vibe-coded with LLM assistance. Use at your own
> risk! I do not agree with a lot of the code structure but I do not care enough
> to "correct" it, as long as it works. I wish this was unnecessary and there
> was an official way to subscribe to these events — hopefully one day it will
> be rendered unnecessary. And yes that m-Dash was me, not the LLM, I know how
> to write, too, sometimes.
>
> I will probably monitor this for a few days and then forget about it. I expect
> this to break somehow if there is a new website layout, paging, a new year, or
> something else the script does not expect. Please open an issue, if you notice
> something.

Automatically generates calendar subscription from [top events in
Nürnberg](https://www.nuernberg.de/internet/stadtportal/veranstaltungen_events_highlights.html).

- Documentation (and FAQ – if any) can found in this README.
- Feel free to file issues to report bugs, ask questions, or request features.
- Feel free to open a pull request.

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
