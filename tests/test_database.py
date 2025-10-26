"""Tests for BBS database operations."""
import pytest
import sqlite3
import bcrypt
import sys
from pathlib import Path

# Add the parent directory to the path so we can import bbs_server
sys.path.insert(0, str(Path(__file__).parent.parent))

import bbs_server


class TestDatabase:
    """Test database operations."""
    
    def test_init_db(self, temp_db):
        """Test database initialization."""
        # Database should be initialized by the fixture
        conn = sqlite3.connect(temp_db)
        c = conn.cursor()
        
        # Check that tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        
        assert 'users' in tables
        assert 'messages' in tables
        conn.close()
    
    def test_create_user(self, temp_db):
        """Test user creation."""
        username = "testuser"
        password = "testpass123"
        
        # Create user
        bbs_server.create_user(username, password)
        
        # Verify user exists
        user_data = bbs_server.get_user(username)
        assert user_data is not None
        
        stored_username, stored_hash = user_data
        assert stored_username == username
        
        # Verify password can be checked
        assert bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        assert not bcrypt.checkpw("wrongpassword".encode('utf-8'), stored_hash)
    
    def test_get_nonexistent_user(self, temp_db):
        """Test getting a user that doesn't exist."""
        user_data = bbs_server.get_user("nonexistent")
        assert user_data is None
    
    def test_post_and_list_messages(self, temp_db):
        """Test posting and listing messages."""
        # Initially no messages
        messages = bbs_server.list_messages()
        assert len(messages) == 0
        
        # Post a message
        author = "testuser"
        body = "This is a test message"
        bbs_server.post_message(author, body)
        
        # Check messages
        messages = bbs_server.list_messages()
        assert len(messages) == 1
        
        msg_author, msg_body, msg_timestamp = messages[0]
        assert msg_author == author
        assert msg_body == body
        assert msg_timestamp is not None
    
    def test_multiple_messages_ordering(self, temp_db):
        """Test that messages are returned in reverse chronological order."""
        messages_data = [
            ("user1", "First message"),
            ("user2", "Second message"),
            ("user3", "Third message"),
        ]
        
        # Post messages
        for author, body in messages_data:
            bbs_server.post_message(author, body)
        
        # Get messages
        messages = bbs_server.list_messages()
        assert len(messages) == 3
        
        # Should be in reverse order (newest first)
        assert messages[0][1] == "Third message"
        assert messages[1][1] == "Second message"
        assert messages[2][1] == "First message"
    
    def test_message_limit(self, temp_db):
        """Test message limit functionality."""
        # Post more messages than the limit
        for i in range(15):
            bbs_server.post_message(f"user{i}", f"Message {i}")
        
        # Default limit should be 10
        messages = bbs_server.list_messages()
        assert len(messages) == 10
        
        # Test custom limit
        messages = bbs_server.list_messages(limit=5)
        assert len(messages) == 5
        
        # Test higher limit
        messages = bbs_server.list_messages(limit=20)
        assert len(messages) == 15  # Only 15 messages exist