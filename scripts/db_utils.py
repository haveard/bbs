#!/usr/bin/env python3
"""
Database management utility for BBS project.
This script provides common database operations for development and maintenance.

Created by: Agent Assistant
Date: 2025-10-26
Usage: uv run python scripts/db_utils.py [command]
"""
import sys
import argparse
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import bbs_server


def reset_database():
    """Reset the database by clearing all data."""
    print("🗑️  Resetting database...")
    
    # Initialize fresh database
    bbs_server.init_db()
    print("✅ Database reset complete.")


def backup_database():
    """Create a backup of the current database."""
    import shutil
    import datetime
    
    db_path = bbs_server.DB_PATH
    if not Path(db_path).exists():
        print("❌ Database file not found.")
        return
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")


def show_stats():
    """Show database statistics."""
    import sqlite3
    
    if not Path(bbs_server.DB_PATH).exists():
        print("❌ Database file not found.")
        return
    
    conn = sqlite3.connect(bbs_server.DB_PATH)
    c = conn.cursor()
    
    # Count users
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    
    # Count messages
    c.execute("SELECT COUNT(*) FROM messages")
    message_count = c.fetchone()[0]
    
    # Get latest message
    c.execute("SELECT posted_at FROM messages ORDER BY id DESC LIMIT 1")
    latest = c.fetchone()
    latest_msg = latest[0] if latest else "None"
    
    conn.close()
    
    print("📊 Database Statistics:")
    print(f"   Users: {user_count}")
    print(f"   Messages: {message_count}")
    print(f"   Latest message: {latest_msg}")


def create_test_data():
    """Create sample test data for development."""
    print("🧪 Creating test data...")
    
    # Create test users
    test_users = [
        ("alice", "password123"),
        ("bob", "securepass"),
        ("charlie", "testpass"),
    ]
    
    for username, password in test_users:
        try:
            bbs_server.create_user(username, password)
            print(f"   Created user: {username}")
        except Exception as e:
            print(f"   User {username} already exists")
    
    # Create test messages
    test_messages = [
        ("alice", "Welcome to our BBS! This is the first message."),
        ("bob", "Hello everyone! Great to be here."),
        ("charlie", "Testing the message system. How does it look?"),
        ("alice", "The system seems to be working well!"),
    ]
    
    for author, body in test_messages:
        bbs_server.post_message(author, body)
        print(f"   Posted message from {author}")
    
    print("✅ Test data created successfully!")


def main():
    """Main script entry point."""
    parser = argparse.ArgumentParser(description='BBS Database Utility')
    parser.add_argument('command', choices=['reset', 'backup', 'stats', 'test-data'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    print(f"🔧 BBS Database Utility")
    print(f"Database: {bbs_server.DB_PATH}")
    print("-" * 40)
    
    if args.command == 'reset':
        reset_database()
    elif args.command == 'backup':
        backup_database()
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'test-data':
        create_test_data()


if __name__ == "__main__":
    main()