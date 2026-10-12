import unittest
from pathlib import Path

from timetable import Entry, Timetable, minutes


class TimetableTests(unittest.TestCase):
    def setUp(self):
        self.database = Path(__file__).with_name(".timetable-test.json")
        self.database.unlink(missing_ok=True)

    def tearDown(self):
        self.database.unlink(missing_ok=True)
        self.database.with_name(self.database.name + ".tmp").unlink(missing_ok=True)

    def test_entries_persist_and_sort_by_weekday_and_time(self):
        timetable = Timetable(self.database)
        timetable.add(Entry("study", "Review", "Tuesday", "15:00", "16:00"))
        timetable.add(Entry("class", "Math", "Monday", "09:00", "10:00"))
        restored = Timetable(self.database)
        self.assertEqual([item.title for item in restored.list_entries()], ["Math", "Review"])

    def test_overlapping_events_are_rejected_but_adjacent_events_allowed(self):
        timetable = Timetable(self.database)
        timetable.add(Entry("class", "Biology", "Monday", "09:00", "10:00"))
        with self.assertRaisesRegex(ValueError, "Time conflict"):
            timetable.add(Entry("exam", "Biology exam", "Monday", "09:30", "10:30"))
        timetable.add(Entry("assignment", "Essay deadline", "Monday", "10:00", "11:00"))

    def test_invalid_times_weekdays_and_empty_titles_are_rejected(self):
        with self.assertRaises(ValueError):
            minutes("9am")
        for entry in (
            Entry("class", "Math", "Funday", "09:00", "10:00"),
            Entry("study", "  ", "Monday", "09:00", "10:00"),
            Entry("exam", "Final", "Monday", "10:00", "09:00"),
        ):
            with self.subTest(entry=entry), self.assertRaises(ValueError):
                entry.validate()


if __name__ == "__main__":
    unittest.main()