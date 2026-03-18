import sqlite3, argparse
from datetime import date, timedelta

# Our database
DB = "habits.db"

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

def add_habit(name):
    db = sqlite3.connect(DB)
    
