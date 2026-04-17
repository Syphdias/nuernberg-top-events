# Agent Guidelines for nuernberg-top-events

## Project Overview

This is a Python project that parses Nürnberg Top Events from the city website and generates an iCal calendar file. It uses `uv` for package management.

## Build & Development Commands

### Testing
```bash
uv run python test_nuernberg_top_events.py -v
```

Run a **single test**:
```bash
uv run python test_nuernberg_top_events.py -v TestDateParsing.test_single_date
```

### Linting & Formatting
```bash
uv run ruff check .        # Lint with ruff
uv run black .            # Format with black
uv run pyright             # Type checking
```

### Running the Application
```bash
uv run nuernberg-top-events --ical      # Generate iCal file
uv run nuernberg-top-events --dry-run   # Print events without saving
uv run nuernberg-top-events --min-events 5  # Adjust minimum event threshold
```

### Dependencies
```bash
uv sync                    # Install all dependencies
uv sync --group dev        # Install dev dependencies
```

## Code Style Guidelines

### Formatting
- Line length: 100 characters
- Use Black for formatting
- Python version: 3.11+

### Imports
Order imports as follows:
1. Standard library (`re`, `dataclasses`, `datetime`, `argparse`, `urllib`)
2. Third-party packages (`icalendar`)

```python
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from icalendar import Calendar, Event
```

### Type Hints
- Use Python 3.11+ union syntax: `datetime | None` (not `Optional[datetime]`)
- Use `str | None` for optional strings

```python
def parse_date_string(date_str: str, year: int | None = None) -> list[EventDate]:
```

### Naming Conventions
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`

### Dataclasses
Use `@dataclass` for simple data structures:

```python
@dataclass
class EventDate:
    start: datetime
    end: datetime | None = None
    month_name: str | None = None
    starts_with_ab: bool = False
```

### Error Handling
- Prefer returning empty collections over raising exceptions for expected error cases
- Use `try/except` with broad `Exception` for external I/O (network requests)
- Print errors to stderr, exit with code 1 for critical failures

```python
try:
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
except Exception:
    return []
```

### Argument Parsing
Use `argparse` with the following patterns:
- `action="store_true"` for boolean flags (`--dry-run`, `--ical`)
- `type=int` with `default` for numeric options

```python
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Print parsed events without generating iCal file",
)
parser.add_argument(
    "--min-events",
    type=int,
    default=10,
    help="Minimum number of events required (default: 10)",
)
```

### Regular Expressions
- Use raw strings (`r"..."`) for regex patterns
- Use `re.search()` for single matches
- Use `re.findall()` for multiple matches
- Use `re.sub()` for replacements

### File Operations
- Use context managers (`with open(...) as f:`)
- Write binary mode (`"wb"`) for iCal files
- Read text mode (`"r"`) for text files

### Docstrings
Use Google-style docstrings:

```python
def parse_date_string(date_str: str, year: int | None = None) -> list[EventDate]:
    """Parse German date string and return list of EventDate objects.
    
    Args:
        date_str: German date string (e.g., "9. August", "24. April 2027")
        year: Year to use if not specified. If None, uses current year.
    
    Returns:
        List of EventDate objects. "und" with different months returns 2.
    """
```

## Project Structure

```
.
├── nuernberg_top_events.py      # Main application code
├── test_nuernberg_top_events.py # Unit tests (unittest)
├── pyproject.toml               # Project configuration
├── .github/workflows/           # GitHub Actions
└── nuernberg_top_events.ical    # Generated calendar output
```

## Linters & Tools Configuration

### ruff (pyproject.toml)
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
```

### black (pyproject.toml)
```toml
[tool.black]
line-length = 100
target-version = ["py311"]
```

### pyright (pyproject.toml)
```toml
[tool.pyright]
typeCheckingMode = "basic"
pythonVersion = "3.11"
```

## Important Notes

**Critical parsing rules:**
- `"bis"` (e.g., "22. Juni bis 2. Juli") → 1 VEVENT (range)
- `"und"` different months (e.g., "26. Juli und 8. August") → 2 VEVENTs (separate)
- `"und"` same month (e.g., "1. und 2. August") → 1 VEVENT (range)
- `"Ab"` (e.g., "Ab 1. Mai") → adds "(ab heute)" suffix in output
- `"Erst wieder"` without specific dates → skipped
- Explicit year in date (e.g., "24. April 2027") → use that year, include in calendar
- Default year = current year (not hardcoded)
- `page_year` check required in `fetch_events_for_year()` to avoid duplicates

- The project was created with LLM assistance ("vibe-coded")
- Generated calendar deployed to GitHub Pages via daily GitHub Action
- Events fetched from: https://www.nuernberg.de/internet/stadtportal/veranstaltungen_events_highlights.html
- iCal DTEND is exclusive (add 1 day to end date)

## CI/CD

GitHub Actions workflow (`.github/workflows/update-calendar.yml`):
- Runs daily at 2 AM UTC
- Can be triggered manually via `workflow_dispatch`
- Deploys iCal to GitHub Pages

## Adding New Dependencies

```bash
uv add <package>           # Add production dependency
uv add --group dev <package>  # Add dev dependency
```
