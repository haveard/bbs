"""Tests for BBS server functionality."""
import pytest
import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import bbs_server
sys.path.insert(0, str(Path(__file__).parent.parent))

import bbs_server


class TestServerFunctions:
    """Test server utility functions."""
    
    @pytest.mark.asyncio
    async def test_active_user_management(self):
        """Test active user tracking."""
        # Clear any existing active users
        async with bbs_server.ACTIVE_LOCK:
            bbs_server.ACTIVE_USERS.clear()
        
        # Initially no active users
        users = await bbs_server.list_active_users()
        assert len(users) == 0
        
        # Add a user
        await bbs_server.add_active_user("testuser1")
        users = await bbs_server.list_active_users()
        assert len(users) == 1
        assert "testuser1" in users
        
        # Add another user
        await bbs_server.add_active_user("testuser2")
        users = await bbs_server.list_active_users()
        assert len(users) == 2
        assert "testuser1" in users
        assert "testuser2" in users
        
        # Remove a user
        await bbs_server.remove_active_user("testuser1")
        users = await bbs_server.list_active_users()
        assert len(users) == 1
        assert "testuser2" in users
        assert "testuser1" not in users
        
        # Remove non-existent user (should not error)
        await bbs_server.remove_active_user("nonexistent")
        users = await bbs_server.list_active_users()
        assert len(users) == 1
        
        # Clear all
        await bbs_server.remove_active_user("testuser2")
        users = await bbs_server.list_active_users()
        assert len(users) == 0
    
    @pytest.mark.asyncio
    async def test_duplicate_active_user(self):
        """Test adding the same user multiple times."""
        # Clear any existing active users
        async with bbs_server.ACTIVE_LOCK:
            bbs_server.ACTIVE_USERS.clear()
        
        # Add user twice
        await bbs_server.add_active_user("testuser")
        await bbs_server.add_active_user("testuser")
        
        # Should only appear once (set behavior)
        users = await bbs_server.list_active_users()
        assert len(users) == 1
        assert "testuser" in users


class TestServerIntegration:
    """Integration tests for the server."""
    
    @pytest.mark.asyncio
    async def test_server_startup_shutdown(self, bbs_server_instance):
        """Test that server starts and stops properly."""
        port = bbs_server_instance
        
        # Server should be running - try to connect
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        
        try:
            result = sock.connect_ex(('127.0.0.1', port))
            assert result == 0  # Connection successful
        finally:
            sock.close()
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_client_connection_and_login(self, bbs_server_instance, bbs_client):
        """Test client connection and login flow."""
        port = bbs_server_instance
        bbs_client.port = port
        
        # Connect to server
        bbs_client.connect()
        
        # Test login with new user
        success = bbs_client.login("testuser", "testpass123")
        assert success
        
        # Logout
        response = bbs_client.logout()
        assert "Logging out" in response
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(15)
    async def test_message_posting_and_reading(self, bbs_server_instance, bbs_client, temp_db):
        """Test posting and reading messages through the server."""
        port = bbs_server_instance
        bbs_client.port = port
        
        # Connect and login
        bbs_client.connect()
        bbs_client.login("messageuser", "password123")
        
        # Post a message
        test_message = "Hello from integration test!"
        response = bbs_client.post_message(test_message)
        assert "Posted" in response
        
        # Read messages
        response = bbs_client.read_messages()
        assert test_message in response
        assert "messageuser" in response
        
        # Logout
        bbs_client.logout()
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(15)
    async def test_who_online_functionality(self, bbs_server_instance, temp_db):
        """Test the who's online functionality."""
        port = bbs_server_instance
        
        # Create two clients
        from tests.conftest import BBSClient
        
        client1 = BBSClient(port=port)
        client2 = BBSClient(port=port)
        
        try:
            # Connect both clients
            client1.connect()
            client2.connect()
            
            # Login both users
            client1.login("user1", "pass1")
            client2.login("user2", "pass2")
            
            # Check who's online from client1
            response = client1.who_online()
            assert "user1" in response
            assert "user2" in response
            
            # Logout client2
            client2.logout()
            client2.disconnect()
            
            # Give server time to process disconnection
            await asyncio.sleep(0.5)
            
            # Check who's online from client1 - user2 should be gone
            response = client1.who_online()
            assert "user1" in response
            
            # Logout client1
            client1.logout()
            
        finally:
            client1.disconnect()
            client2.disconnect()
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(10)
    async def test_invalid_login(self, bbs_server_instance, bbs_client):
        """Test login with invalid credentials."""
        port = bbs_server_instance
        bbs_client.port = port
        
        # Connect to server
        bbs_client.connect()
        
        # Create a user first
        bbs_client.login("realuser", "realpass")
        bbs_client.logout()
        bbs_client.disconnect()
        
        # Reconnect and try wrong password
        bbs_client.connect()
        
        # Wait for welcome and username prompt
        bbs_client.recv_until("Username: ")
        
        # Send existing username
        bbs_client.send("realuser")
        
        # Should ask for password
        bbs_client.recv_until("Password: ")
        
        # Send wrong password
        bbs_client.send("wrongpass")
        
        # Should get login failed
        response = bbs_client.recv_until("Goodbye", timeout=3)
        assert "Login failed" in response or "Goodbye" in response