# Student Timetable Planner

A dependency-free Python 3.13 CLI that persistently schedules classes, assignments, exams, and study sessions in a weekly timetable. It validates weekdays and 24-hour time ranges, rejects overlapping events on the same day, and permits adjacent events. Data defaults to `%USERPROFILE%\.student-timetable\timetable.json`, not the source folder.

## Use

```powershell
py -3.13 timetable.py add class "Calculus" Monday 09:00 10:30
py -3.13 timetable.py add assignment "Problem set 1" Tuesday 16:00 17:00
py -3.13 timetable.py add exam "Biology midterm" Friday 13:00 15:00
py -3.13 timetable.py add study "Review notes" Sunday 10:00 11:00
py -3.13 timetable.py list
```

Choose a weekday from Monday through Sunday and use `HH:MM` in 24-hour time. Supply `--database path\to\file.json` before the subcommand to use a different store.

## Test

```powershell
py -3.13 -m unittest discover -s tests -v
```