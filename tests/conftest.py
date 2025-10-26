import pytest
import asyncio
import socket
import sqlite3
import tempfile
import os
import threading
import time
from pathlib import Path
import sys

# Add the parent directory to the path so we can import bbs_server
sys.path.insert(0, str(Path(__file__).parent.parent))

import bbs_server

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Set the DB_PATH for testing
    original_db_path = bbs_server.DB_PATH
    bbs_server.DB_PATH = db_path
    
    # Initialize the test database
    bbs_server.init_db()
    
    yield db_path
    
    # Cleanup
    bbs_server.DB_PATH = original_db_path
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
async def bbs_server_instance(temp_db):
    """Start a BBS server instance for testing."""
    # Find an available port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()
    
    # Set up server
    original_port = bbs_server.BBS_PORT
    bbs_server.BBS_PORT = port
    
    # Start server
    server = await asyncio.start_server(
        bbs_server.session_task,
        host="127.0.0.1",
        port=port,
        start_serving=True
    )
    
    yield port
    
    # Cleanup
    server.close()
    await server.wait_closed()
    bbs_server.BBS_PORT = original_port
    
    # Clear active users
    async with bbs_server.ACTIVE_LOCK:
        bbs_server.ACTIVE_USERS.clear()

class BBSClient:
    """Helper class for testing BBS client interactions."""
    
    def __init__(self, host='localhost', port=2323):
        self.host = host
        self.port = port
        self.sock = None
    
    def connect(self):
        """Connect to the BBS server."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5.0)
        self.sock.connect((self.host, self.port))
    
    def disconnect(self):
        """Disconnect from the BBS server."""
        if self.sock:
            self.sock.close()
            self.sock = None
    
    def send(self, data):
        """Send data to the server."""
        if self.sock is None:
            raise RuntimeError("Not connected")
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.sock.send(data + b'\n')
    
    def recv(self, size=1024):
        """Receive data from the server."""
        if self.sock is None:
            raise RuntimeError("Not connected")
        return self.sock.recv(size).decode('utf-8', errors='ignore')
    
    def recv_until(self, expected, timeout=5):
        """Receive data until expected string is found."""
        if self.sock is None:
            raise RuntimeError("Not connected")
            
        buffer = ""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                data = self.sock.recv(1024).decode('utf-8', errors='ignore')
                if not data:
                    break
                buffer += data
                if expected in buffer:
                    return buffer
                time.sleep(0.1)
            except socket.timeout:
                break
        
        return buffer
    
    def login(self, username, password):
        """Complete login flow."""
        # Wait for welcome and username prompt
        self.recv_until("Username: ")
        
        # Send username
        self.send(username)
        
        # Check if new user or existing user
        response = self.recv_until(":", timeout=10)  # Wait for either "password:" or "Create password:"
        
        if "Create password:" in response:
            # New user flow
            self.send(password)
            # Wait for user created message and menu
            self.recv_until("Choice?> ", timeout=10)
        elif "Password:" in response:
            # Existing user flow
            self.send(password)
            response = self.recv_until("Choice?> ", timeout=10)
            if "Login failed" in response:
                return False
        
        return True
    
    def post_message(self, message):
        """Post a message."""
        self.send("2")  # Select post message
        self.recv_until("> ")  # Wait for message prompt
        self.send(message)
        return self.recv_until("Choice?> ")  # Wait for menu
    
    def read_messages(self):
        """Read messages."""
        self.send("1")  # Select read messages
        response = self.recv_until("Choice?> ")
        return response
    
    def who_online(self):
        """Check who's online."""
        self.send("3")  # Select who's online
        response = self.recv_until("Choice?> ")
        return response
    
    def logout(self):
        """Logout."""
        self.send("4")  # Select logout
        return self.recv(1024)

@pytest.fixture
def bbs_client():
    """Create a BBS client for testing."""
    client = BBSClient()
    yield client
    client.disconnect()