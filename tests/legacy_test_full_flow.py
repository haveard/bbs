#!/usr/bin/env python3
import socket
import time
import threading

def test_message_flow():
    """Test the complete flow: login, post message, read messages"""
    try:
        print("🔌 Connecting to BBS server...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 2323))
        sock.settimeout(5.0)  # 5 second timeout
        
        def recv_until_prompt(expected_prompt="Choice?> "):
            """Receive data until we see the expected prompt"""
            buffer = ""
            while True:
                try:
                    data = sock.recv(1024).decode('utf-8', errors='ignore')
                    if not data:
                        break
                    buffer += data
                    print(data, end='', flush=True)
                    if expected_prompt in buffer:
                        break
                    time.sleep(0.1)
                except socket.timeout:
                    break
            return buffer
        
        # Receive welcome and username prompt
        print("📝 Waiting for welcome message...")
        data = recv_until_prompt("Username: ")
        
        # Send username
        username = "messagetest"
        print(f"\n➡️  Sending username: {username}")
        sock.send(f"{username}\n".encode())
        time.sleep(0.5)
        
        # Receive password prompt (new user or existing)
        data = recv_until_prompt("Choice?> ")
        
        if "New user" in data:
            print("🆕 Creating new user...")
            password = "testpass123"
            sock.send(f"{password}\n".encode())
            time.sleep(0.5)
            # Wait for menu after user creation
            recv_until_prompt("Choice?> ")
        
        # Now we should be at the main menu
        print("\n🎯 At main menu - posting a message...")
        
        # Select option 2 (Post a message)
        sock.send(b"2\n")
        time.sleep(0.5)
        
        # Wait for message prompt
        data = recv_until_prompt("> ")
        
        # Send a test message
        test_message = "Hello from the automated test! This is a test message."
        print(f"➡️  Posting message: '{test_message}'")
        sock.send(f"{test_message}\n".encode())
        time.sleep(0.5)
        
        # Wait for confirmation and return to menu
        data = recv_until_prompt("Choice?> ")
        
        # Now read messages to verify our message was posted
        print("\n📖 Reading messages to verify...")
        sock.send(b"1\n")
        time.sleep(0.5)
        
        # Read the messages
        data = recv_until_prompt("Choice?> ")
        
        if test_message in data:
            print("✅ SUCCESS: Message was posted and retrieved!")
        else:
            print("❌ ERROR: Message was not found in the message list")
        
        # Check who's online
        print("\n👥 Checking who's online...")
        sock.send(b"3\n")
        time.sleep(0.5)
        
        data = recv_until_prompt("Choice?> ")
        
        if username in data:
            print(f"✅ SUCCESS: User '{username}' is shown as online!")
        else:
            print(f"❌ ERROR: User '{username}' not shown in online list")
        
        # Logout
        print("\n🚪 Logging out...")
        sock.send(b"4\n")
        time.sleep(0.5)
        
        # Receive logout message
        try:
            data = sock.recv(1024).decode('utf-8', errors='ignore')
            print(data)
        except:
            pass
        
        sock.close()
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_concurrent_users():
    """Test multiple users connecting simultaneously"""
    print("\n🔄 Testing concurrent users...")
    
    def user_session(username, message):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 2323))
            sock.settimeout(3.0)
            
            # Skip welcome, send username
            time.sleep(0.5)
            sock.send(f"{username}\n".encode())
            time.sleep(0.5)
            
            # Send password (new user)
            sock.send(f"pass{username}\n".encode())
            time.sleep(0.5)
            
            # Skip to menu, post message
            sock.send(b"2\n")
            time.sleep(0.5)
            sock.send(f"{message}\n".encode())
            time.sleep(0.5)
            
            # Logout
            sock.send(b"4\n")
            time.sleep(0.5)
            sock.close()
            
            print(f"✅ User {username} completed session")
        except Exception as e:
            print(f"❌ User {username} failed: {e}")
    
    # Start 3 concurrent user sessions
    threads = []
    for i in range(3):
        username = f"user{i}"
        message = f"Message from {username} - concurrent test!"
        thread = threading.Thread(target=user_session, args=(username, message))
        threads.append(thread)
        thread.start()
    
    # Wait for all to complete
    for thread in threads:
        thread.join()
    
    print("✅ Concurrent user test completed")

if __name__ == "__main__":
    print("🧪 Testing BBS Message Flow\n")
    
    # Test main message flow
    test_message_flow()
    
    # Test concurrent users
    test_concurrent_users()
    
    print("\n🔍 Final database check:")
    import subprocess
    subprocess.run(["uv", "run", "python", "check_db.py"])