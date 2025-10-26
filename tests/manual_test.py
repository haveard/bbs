#!/usr/bin/env python3
"""
Manual testing script for BBS functionality.
Run this to test the BBS manually without automated tests.
"""
import sys
from pathlib import Path

# Add the parent directory to the path so we can import bbs_server
sys.path.insert(0, str(Path(__file__).parent.parent))

import bbs_server


def check_database(db_path="./data/bbs.sqlite3"):
    """Check database contents for manual inspection."""
    import sqlite3
    import os
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check users
    c.execute("SELECT username, created_at FROM users")
    users = c.fetchall()
    print("Users in database:")
    for user, created in users:
        print(f"  - {user} (created: {created})")
    
    # Check messages
    c.execute("SELECT author, body, posted_at FROM messages ORDER BY id DESC")
    messages = c.fetchall()
    print(f"\nMessages in database ({len(messages)} total):")
    if messages:
        for author, body, posted in messages:
            print(f"  - [{posted}] {author}: {body}")
    else:
        print("  - No messages yet")
    
    conn.close()


def create_test_data():
    """Create some test data for manual testing."""
    print("Creating test data...")
    
    # Create test users
    test_users = [
        ("alice", "password123"),
        ("bob", "securepass"),
        ("charlie", "testpass"),
    ]
    
    for username, password in test_users:
        try:
            bbs_server.create_user(username, password)
            print(f"Created user: {username}")
        except Exception as e:
            print(f"User {username} might already exist: {e}")
    
    # Create test messages
    test_messages = [
        ("alice", "Welcome to our BBS! This is the first message."),
        ("bob", "Hello everyone! Great to be here."),
        ("charlie", "Testing the message system. How does it look?"),
        ("alice", "The system seems to be working well!"),
        ("bob", "Anyone know how to use the advanced features?"),
    ]
    
    for author, body in test_messages:
        bbs_server.post_message(author, body)
        print(f"Posted message from {author}")
    
    print("Test data created successfully!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create-data":
        create_test_data()
    
    check_database()