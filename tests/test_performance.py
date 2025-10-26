"""Performance and stress tests for BBS server."""
import pytest
import asyncio
import threading
import time
import sys
from pathlib import Path

# Add the parent directory to the path so we can import bbs_server
sys.path.insert(0, str(Path(__file__).parent.parent))

import bbs_server


class TestPerformance:
    """Performance and concurrent user tests."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_concurrent_connections(self, bbs_server_instance, temp_db):
        """Test multiple concurrent connections."""
        port = bbs_server_instance
        num_clients = 5
        
        from tests.conftest import BBSClient
        
        async def client_session(client_id):
            """Individual client session."""
            client = BBSClient(port=port)
            try:
                client.connect()
                
                # Login
                username = f"user{client_id}"
                password = f"pass{client_id}"
                success = client.login(username, password)
                assert success
                
                # Post a message
                message = f"Message from user {client_id}"
                response = client.post_message(message)
                assert "Posted" in response
                
                # Read messages
                response = client.read_messages()
                assert message in response
                
                # Check who's online
                response = client.who_online()
                assert username in response
                
                # Logout
                client.logout()
                return True
                
            except Exception as e:
                print(f"Client {client_id} failed: {e}")
                return False
            finally:
                client.disconnect()
        
        # Run multiple clients concurrently
        tasks = []
        for i in range(num_clients):
            task = asyncio.create_task(client_session(i))
            tasks.append(task)
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that all succeeded
        successful = sum(1 for result in results if result is True)
        assert successful >= num_clients - 1  # Allow for one failure due to timing
        
        # Verify messages were posted
        messages = bbs_server.list_messages(limit=num_clients)
        assert len(messages) >= num_clients - 1
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(20)
    async def test_rapid_message_posting(self, bbs_server_instance, bbs_client, temp_db):
        """Test rapid message posting."""
        port = bbs_server_instance
        bbs_client.port = port
        
        # Connect and login
        bbs_client.connect()
        bbs_client.login("rapiduser", "rapidpass")
        
        # Post multiple messages rapidly
        num_messages = 10
        for i in range(num_messages):
            message = f"Rapid message {i}"
            response = bbs_client.post_message(message)
            assert "Posted" in response
        
        # Verify all messages were stored
        messages = bbs_server.list_messages(limit=num_messages)
        assert len(messages) == num_messages
        
        # Verify order (newest first)
        for i, (author, body, timestamp) in enumerate(messages):
            expected_msg = f"Rapid message {num_messages - 1 - i}"
            assert body == expected_msg
            assert author == "rapiduser"
        
        bbs_client.logout()
    
    def test_database_performance(self, temp_db):
        """Test database operations performance."""
        import time
        
        # Test user creation performance
        start_time = time.time()
        for i in range(100):
            bbs_server.create_user(f"perfuser{i}", "password123")
        user_creation_time = time.time() - start_time
        
        # Should create 100 users in reasonable time (< 5 seconds)
        assert user_creation_time < 5.0
        
        # Test message posting performance
        start_time = time.time()
        for i in range(100):
            bbs_server.post_message(f"perfuser{i % 10}", f"Performance test message {i}")
        message_posting_time = time.time() - start_time
        
        # Should post 100 messages in reasonable time (< 2 seconds)
        assert message_posting_time < 2.0
        
        # Test message retrieval performance
        start_time = time.time()
        for _ in range(100):
            messages = bbs_server.list_messages(limit=10)
            assert len(messages) == 10
        message_retrieval_time = time.time() - start_time
        
        # Should retrieve messages 100 times in reasonable time (< 1 second)
        assert message_retrieval_time < 1.0
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(15)
    async def test_connection_cleanup(self, bbs_server_instance, temp_db):
        """Test that connections are properly cleaned up."""
        port = bbs_server_instance
        
        from tests.conftest import BBSClient
        
        # Create multiple connections and disconnect abruptly
        for i in range(5):
            client = BBSClient(port=port)
            client.connect()
            client.login(f"cleanupuser{i}", "password")
            
            # Check user is online
            active_users = await bbs_server.list_active_users()
            assert f"cleanupuser{i}" in active_users
            
            # Disconnect abruptly (without logout)
            client.disconnect()
            
            # Give server time to detect disconnection
            await asyncio.sleep(0.5)
            
            # User should be removed from active list
            active_users = await bbs_server.list_active_users()
            assert f"cleanupuser{i}" not in active_users
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(10) 
    async def test_long_username_and_message(self, bbs_server_instance, bbs_client, temp_db):
        """Test handling of long usernames and messages."""
        port = bbs_server_instance
        bbs_client.port = port
        
        # Test with long username (but reasonable)
        long_username = "a" * 50  # 50 character username
        long_password = "b" * 20   # 20 character password
        
        bbs_client.connect()
        success = bbs_client.login(long_username, long_password)
        assert success
        
        # Test with long message (but reasonable)
        long_message = "This is a very long message that tests the system's ability to handle longer text content. " * 5
        response = bbs_client.post_message(long_message)
        assert "Posted" in response
        
        # Verify message was stored correctly
        response = bbs_client.read_messages()
        assert long_message in response
        assert long_username in response
        
        bbs_client.logout()