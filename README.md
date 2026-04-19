# Daily Habit Tracker
#### Video Demo: https://www.youtube.com/watch?v=Ca7LJ_hPAKQ
#### Description:

This Daily Habit Tracker is a command-line application written in Python that helps you build and maintain daily habits. It lets you add habits you want to track, log which ones you completed each day, view your current streaks, and see detailed statistics over any time period. Everything is stored locally in a SQLite database file, so your data persists between sessions without needing any external service, or evem internet connection.

## Why I Built It This Way

I wanted to build something genuinely useful rather than just a demo project. A habit tracker is something I could actually use day to day, and building it as a command-line tool felt like the right choice — it's fast to open, fast to use, and doesn't require a browser or a GUI. The command-line interface also gave me a good opportunity to work with `argparse`, Python's built-in library for handling command-line arguments, which made the program feel like a real tool rather than just a script.

For the database I chose SQLite because it's lightweight, requires no setup, and stores everything in a single `.db` file that lives right next to the program. I considered just storing data in a CSV file, but a database made much more sense once I thought about the kind of queries I'd need — filtering by date range, counting completions, finding streaks — all things SQL handles naturally.

## Files

### `habits.py`

This is the only source file in the project. It contains all the logic for the application, organized into clearly separated functions:

**`setup_database()`** — Runs once on every launch to make sure the database and its tables exist. It uses `CREATE TABLE IF NOT EXISTS` so it's safe to run repeatedly without wiping any existing data. It creates two tables: `habits`, which stores the name of each habit with a unique ID, and `logs`, which records every time a habit is marked as completed on a given day.

**`add_habit(name)`** — Inserts a new habit into the `habits` table. If a habit with the same name already exists, SQLite raises an `IntegrityError` because the `name` column has a `UNIQUE` constraint, and the program catches it and prints a friendly message instead of crashing.

**`delete_habit()`** — Shows a numbered list of all habits and lets the user pick one to delete. It asks for confirmation before deleting, and importantly deletes the habit's log history first before deleting the habit itself, to avoid leaving orphaned rows in the logs table.

**`calculate_streak(habit_id)`** — Calculates the current streak for a given habit by walking backwards through dates starting from today, checking the database for a log entry on each day, and stopping as soon as it finds a day with no entry. This gives you the number of consecutive days the habit has been completed up to and including today.

**`log_today()`** — The main daily-use function. It displays all habits with their current streaks, lets the user enter which ones they completed today as a space-separated list of numbers, and saves those completions to the database. It uses `INSERT OR IGNORE` so that running it twice in a day won't create duplicate entries. After saving, it prints an updated streak for each completed habit.

**`show_stats(days)`** — Displays a formatted table of statistics for all habits over a given time period. For each habit it shows how many days it was completed out of the total days in the range, the completion rate as a percentage, and the best streak recorded. The default time period is 7 days, but can also be a specific number of days like 30 or `"all"` to look at the entire history. When `"all"` is passed, it finds the earliest log entry in the database using `SELECT MIN(day)` to determine the start of the range.

**`main()`** — Sets up `argparse` with three possible commands: `add`, `delete`, `stats`, and a default (no command) that runs `log_today()`. It calls `setup_database()` on every run to ensure the database is always ready, then routes to the appropriate function based on what command was given.

### `habits.db`

This file is automatically created on the first run. It's the SQLite database that stores all your habits and logs. You don't need to create or edit it manually — the program manages it entirely. If you want to start fresh, you can simply delete this file.

## How to Use

```
python3 habits.py                  # log today's habits
python3 habits.py add "habit name" # add a new habit
python3 habits.py delete           # delete a habit
python3 habits.py stats            # view stats for last 7 days
python3 habits.py stats --days 30  # view stats for last 30 days
python3 habits.py stats --days all # view all-time stats
```

## Final Remarks

Although this isn't the most sophisticated project and can definitely be improved with more features or better aesthetics, I feel very proud of this project for a few reasons. Firstly, this is the first project I've done that includes more than just Python. It combines SQL with Python, which greatly increased the complexity but also the ideas and opportunities. Secondly, I was able to expand my knowledge much more than I expected. I didn't know exactly how to do many things, but by reading documentations or watching videos on YouTube, I could figure things out little by little. 

But most importantly, I overcame some big mental obstacles with this. This is my final project for Harvard's CS50x, which I had taken online at my own pace, and I actually finished the lectures and problem sets back in December. I had planned on finishing it before the end of the year, but the idea of creating a whole project sophisticated enough to be worthy of a final project for Harvard felt daunting on me. I felt I didn't have enough capabilities to do such a thing, and I essentially gave up on the idea. I completed the entirety of Harvard's CS50P course before coming back, and finally said screw it and just started typing, until we had this program. 