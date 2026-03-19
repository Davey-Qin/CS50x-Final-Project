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



    

    
