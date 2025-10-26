#!/usr/bin/env python3
import socket
import time

def test_bbs():
    try:
        # Connect to the BBS
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 2323))
        
        # Receive welcome message
        data = sock.recv(1024)
        print("Welcome received:", data.decode('utf-8', errors='ignore'))
        
        # Send username
        sock.send(b'testuser\n')
        time.sleep(0.1)
        
        # Receive prompt for new user
        data = sock.recv(1024)
        print("User prompt:", data.decode('utf-8', errors='ignore'))
        
        # Send password for new user
        sock.send(b'password123\n')
        time.sleep(0.1)
        
        # Receive user created confirmation and menu
        data = sock.recv(1024)
        print("User created:", data.decode('utf-8', errors='ignore'))
        
        # Read any additional data (menu)
        data = sock.recv(1024)
        print("Menu:", data.decode('utf-8', errors='ignore'))
        
        # Select option 2 (post message)
        sock.send(b'2\n')
        time.sleep(0.1)
        
        # Receive post message prompt
        data = sock.recv(1024)
        print("Post prompt:", data.decode('utf-8', errors='ignore'))
        
        # Send a test message
        sock.send(b'Hello from the test client!\n')
        time.sleep(0.1)
        
        # Receive confirmation
        data = sock.recv(1024)
        print("Post confirmation:", data.decode('utf-8', errors='ignore'))
        
        # Read menu again
        data = sock.recv(1024)
        print("Menu again:", data.decode('utf-8', errors='ignore'))
        
        # Select option 1 (read messages)
        sock.send(b'1\n')
        time.sleep(0.1)
        
        # Receive messages
        data = sock.recv(1024)
        print("Messages:", data.decode('utf-8', errors='ignore'))
        
        # Read menu again
        data = sock.recv(1024)
        print("Menu again:", data.decode('utf-8', errors='ignore'))
        
        # Select option 4 (logout)
        sock.send(b'4\n')
        time.sleep(0.1)
        
        # Receive logout message
        data = sock.recv(1024)
        print("Logout:", data.decode('utf-8', errors='ignore'))
        
        sock.close()
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_bbs()