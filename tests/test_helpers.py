#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = "./data/bbs.sqlite3"

def check_database():
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check users
    c.execute("SELECT username, created_at FROM users")
    users = c.fetchall()
    print("Users in database:")
    for user, created in users:
        print(f"  - {user} (created: {created})")
    
    # Check messages
    c.execute("SELECT author, body, posted_at FROM messages")
    messages = c.fetchall()
    print("\nMessages in database:")
    if messages:
        for author, body, posted in messages:
            print(f"  - [{posted}] {author}: {body}")
    else:
        print("  - No messages yet")
    
    conn.close()

if __name__ == "__main__":
    check_database()