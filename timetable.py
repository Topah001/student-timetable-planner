"""Persist and manage weekly classes, assignments, exams, and study sessions."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
KINDS = ("class", "assignment", "exam", "study")
TIME_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


def minutes(value: str) -> int:
    if not TIME_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid time {value!r}; use 24-hour HH:MM.")
    hour, minute = map(int, value.split(":"))
    return hour * 60 + minute


@dataclass(frozen=True)
class Entry:
    kind: str
    title: str
    weekday: str
    start: str
    end: str

    def validate(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"Kind must be one of: {', '.join(KINDS)}.")
        if not self.title.strip() or len(self.title) > 120:
            raise ValueError("Title must contain 1 to 120 non-whitespace characters.")
        if self.weekday not in WEEKDAYS:
            raise ValueError(f"Weekday must be one of: {', '.join(WEEKDAYS)}.")
        if minutes(self.start) >= minutes(self.end):
            raise ValueError("End time must be later than start time on the same day.")


class Timetable:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save([])

    def _load(self) -> list[Entry]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            entries = [Entry(**item) for item in raw]
            for entry in entries:
                entry.validate()
            return entries
        except (OSError, json.JSONDecodeError, TypeError, KeyError, ValueError) as exc:
            raise RuntimeError(f"Could not load timetable {self.path}: {exc}") from exc

    def _save(self, entries: list[Entry]) -> None:
        pending = self.path.with_name(self.path.name + ".tmp")
        pending.write_text(json.dumps([asdict(item) for item in entries], indent=2), encoding="utf-8")
        pending.replace(self.path)

    def add(self, entry: Entry) -> None:
        entry.validate()
        entries = self._load()
        new_start, new_end = minutes(entry.start), minutes(entry.end)
        for existing in entries:
            if existing.weekday == entry.weekday and new_start < minutes(existing.end) and minutes(existing.start) < new_end:
                raise ValueError(
                    f"Time conflict with {existing.kind} '{existing.title}' "
                    f"({existing.start}-{existing.end} on {existing.weekday})."
                )
        entries.append(entry)
        entries.sort(key=lambda item: (WEEKDAYS.index(item.weekday), minutes(item.start)))
        self._save(entries)

    def list_entries(self) -> list[Entry]:
        return self._load()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path.home() / ".student-timetable" / "timetable.json")
    actions = parser.add_subparsers(dest="action", required=True)
    add = actions.add_parser("add", help="Add a scheduled item")
    add.add_argument("kind", choices=KINDS)
    add.add_argument("title")
    add.add_argument("weekday", choices=WEEKDAYS)
    add.add_argument("start", help="Start time, 24-hour HH:MM")
    add.add_argument("end", help="End time, 24-hour HH:MM")
    actions.add_parser("list", help="List all saved items")
    args = parser.parse_args(argv)
    timetable = Timetable(args.database)
    try:
        if args.action == "add":
            entry = Entry(args.kind, args.title, args.weekday, args.start, args.end)
            timetable.add(entry)
            print(f"Added {entry.kind}: {entry.title} ({entry.weekday} {entry.start}-{entry.end}).")
        else:
            entries = timetable.list_entries()
            if not entries:
                print("No timetable items yet. Add one with the 'add' command.")
            for item in entries:
                print(f"{item.weekday:9} {item.start}-{item.end}  {item.kind:10} {item.title}")
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())