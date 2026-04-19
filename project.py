import sqlite3, argparse
from datetime import date, timedelta

# Our database
DB = "habits.db"

# Create tables if not done, consists of two tables: habits, and logs
def setup_database():
    db = sqlite3.connect(DB)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS habits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE    
        );

        CREATE TABLE IF NOT EXISTS logs (
            habit_id INTEGER,
            day TEXT,
            PRIMARY KEY (habit_id, day),
            FOREIGN KEY(habit_id) REFERENCES habits(id)
        );
                     
        
    """)
    db.commit()
    db.close()

# Add habit into habits table
def add_habit(name):
    db = sqlite3.connect(DB)

    try:
        db.execute("INSERT INTO habits (name) VALUES (?)", (name,))
        db.commit()
        print(f"Added {name} as a habit")
    except sqlite3.IntegrityError:
        print(f"You already have a habit called '{name}'")
    db.close()

def delete_habit():
    db = sqlite3.connect(DB)
    # Allow dictionary-like access
    db.row_factory = sqlite3.Row
    habits = db.execute("SELECT * FROM habits ORDER BY id").fetchall()

    #if empty do nothing
    if not habits:
        print("No habits to delete. Add with: python habits.py add 'name")
        db.close()
        return
    
    print("\nYour habits:")
    for i, h in enumerate(habits, 1):
        print(f"{i}. {h['name']}")

    print("\nEnter the number to delete or 0 to cancel: ", end="")
    
    #validate input
    try: 
        choice = int(input())
    except ValueError:
        print("Invalid input.")
        db.close()
        return
    if choice < 1 or choice > len(habits):
        print("Number out of range.")
        db.close()
        return
    if choice == 0:
        print("Cancelled.")
        db.close()
        return
    
    selected = habits[choice - 1]

    print(f"Delete '{selected['name']}' as a habit? (y/n) ", end="")
    confirm = input().strip().lower()

    if confirm == "y":
        db.execute("DELETE FROM logs WHERE habit_id = ?", (selected["id"],))
        db.execute("DELETE FROM habits WHERE id = ?", (selected["id"],))
        db.commit()
        print(f"Deleted '{selected['name']}' as a habit.")
    else:
        print("Cancelled.")
    
    db.close()

def calculate_streak(habit_id):
    db = sqlite3.connect(DB)
    today = date.today()
    streak = 0

    current_day = today

    # While the row in database isnt empty, add to streak
    while True:
        day = current_day.isoformat()
        row = db.execute(
            # Will return true/false if a row is found
            "SELECT 1 FROM logs WHERE habit_id = ? AND day = ?",
            (habit_id, day)
        ).fetchone()

        if row:
            streak += 1
            # Go back a day
            current_day -= timedelta(days=1)
        else:
            break
    
    db.close()
    return streak

def log_today():
    #Get all habits, allow dictionary-like access
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    habits = db.execute("SELECT * FROM habits ORDER BY id").fetchall()
    
    # return if no habits yet
    if not habits:
        print("\nNo habits yet. Add with:  python habits.py add <habits name>")
        db.close() 
        return

    today = date.today().isoformat()   
    print(f"\nHey there! Today is {date.today().strftime('%A, %B %d, %Y')}")

    #show each habit with its streak
    print("Your habits: ")
    for i, h in enumerate(habits, 1):
        streak = calculate_streak(h["id"])
        display = ""
        if streak > 0:
            display = f"🔥 {streak} day streak" 
        else:
            display = "❌ no streak"
        print(f"{i}. {h['name']:<30} {display}")

    # Let user say which ones to check off
    print("What did you complete today?")
    print("Enter numbers seperated by spaces or 0 for none: ", end="")

    # Try user data
    nums = input().strip()

    if nums == "0" or nums == "":
        completed = []
    else:
        #try to seperate on spaces
        try:
            completed = [int(x) for x in nums.split()]
        except ValueError:
            print("Invalid input, please enter numbers seperated by spaces only")
            db.close()
            return
    
    #make sure numbers are in range
    for num in completed:
        if num < 1 or num > len(habits):
            print(f"{num} is not a valid habit number.")
            db.close()
            return
    
    #save to database, ignoring if already logged
    for num in completed:
        habit = habits[num - 1]
        db.execute("INSERT OR IGNORE INTO logs (habit_id, day) VALUES (?, ?)", 
        (habit["id"], today))

    db.commit()

    #show updates
    print(f"\nSuccessfully logged. {len(completed)}/{len(habits)} completed today.")

    for num in completed:
        habit = habits[num - 1]
        streak = calculate_streak(habit["id"])
        print(f"{habit['name']}: 🔥 {streak} day streak")
        
    print()
    db.close()      


# Show stats based of either "all" or given number of days
def show_stats(days):
    #Same procedure, make data dict-like accessible, check if empty
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    habits = db.execute("SELECT * FROM habits ORDER BY id").fetchall()

    if not habits:
        print("\nNo habits yet. Add one with: python habits.py add <habit>")
        db.close()
        return
    
    today = date.today()

    # If print all days, find range to look at
    if days == "all":
        earliest = db.execute("SELECT MIN(day) FROM logs").fetchone()[0]
        if earliest is None:
            print("No logs yet, start logging with python habits.py")
            db.close()
            return
        start_date = date.fromisoformat(earliest)
        period_label = "All time"
    else:
        start_date = today - timedelta(days=days - 1)
        period_label = f"Last {days} days"

    #calculate total days in that range
    total_days = (today - start_date).days + 1

    print(f"\nHabit stats - {period_label}: {start_date} to {today}")
    print(f"  {'Habit':<30} {'Completed':<12} {'Rate':<8} {'Best Streak'}")
    print(f"  {'-'*30} {'-'*12} {'-'*8} {'-'*11}")
        
    # get stats on each habit
    for habit in habits:
        #count how many days this was logged in total range
        completed_count = db.execute("""
            SELECT COUNT(*) FROM logs WHERE habit_id = ?
                AND day >= ? AND day <= ?
            """, (habit["id"], start_date.isoformat(), today.isoformat())).fetchone()[0]
        
        #percentage logged
        rate = int(completed_count / total_days * 100)

        #calculate best streak for this habit
        all_days = db.execute(
            "SELECT day FROM logs WHERE habit_id = ? ORDER BY day", (habit["id"],)
        ).fetchall()

        best_streak = 0
        current_streak = 0
        prev_day = None

        for row in all_days:
            this_day = date.fromisoformat(row["day"])
            if prev_day is None:
                current_streak = 1
            elif (this_day - prev_day).days == 1:
                # continue streak
                current_streak += 1
            else:
                #gap found, reset streak
                current_streak = 1
            best_streak = max(best_streak, current_streak)
            prev_day = this_day
    
        print(f"{habit['name']:<30} {completed_count}/{total_days:<10} {rate}%{'':<5} {best_streak} days")
    db.close()

def main():
    #need argparser
    parser = argparse.ArgumentParser(
        prog="habits",
        description="A handy habit tracker"
    )
    # command options: add, delete, stats
    #if none given, just print a log of habits
    subparsers = parser.add_subparsers(dest="command")

    #add command line optional arguments, with help
    add_parser = subparsers.add_parser("add", help="Add a new habit")
    add_parser.add_argument("name", type=str, help="The name of the habit")

    subparsers.add_parser("delete", help="Delete a habit")

    stats_parser = subparsers.add_parser("stats", help="View habit stats")
    stats_parser.add_argument(
        "--days",
        default="7",
        help="Number of days to show stats for: 7, 30, or all (defaultz: 7)"
    )

    args = parser.parse_args()

    #make sure everything exists and is set up
    setup_database()

    if args.command == "add":
        add_habit(args.name)
    elif args.command == "delete":
        delete_habit()
    elif args.command == "stats":
        if args.days == "all":
            show_stats("all")
        else:
            #convert the string to integer
            try:
                show_stats(int(args.days))
            except ValueError:
                print("days must be a number or all. Example: --days 30")
    else:
        #no commands given
        log_today()

if __name__ == "__main__":
    main()












    

    
