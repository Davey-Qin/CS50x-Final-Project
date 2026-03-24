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
            FOREIGN KEY(habit_id) REFERNCES habits(id)
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
        printf(f"You already have a habit called '{name}'")
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

    print(f"Delete '{selected}' as a habit?", end="")
    confirm = input().strip().lower()

    if confirm == "y":
        db.execute("DELETE FROM logs WHERE habit_id = ?", (selected["id"],))
        db.execute("DELETE FROM habits WHERE id = ?", (selected["id"],))
        db.commit()
        print(f"Deleted '{selected["name"]}' as a habit.")
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
            "SELECT 1 FROM logs WHERE habit_id = ? AND day = ?"
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

    today = date.todat().isoformat()   
    print(f"\nHey there! Today is {date.todat().strftime('%A, %B, %d, %Y')}")

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
    print("What did you completet today?")
    print("Enter numbers seperated by spaces, or 0 for none: ", end="")

    # Try user data
    nums = input().strip()

    if nums == "0" or nums == "":
        completed = []
    else:
        #try to seperate on spaces
        try:
            completed = [int(x) for x in nums.split()]
        except ValueError:
            print("Invalid input please enter numbers seperated by spaces only")
            db.close()
            return
    
    #make sure numbers are in range
    for num in nums:
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







    

    
