import asyncio
import datetime
import os
import sqlite3
import bcrypt
import textwrap
import signal
import sys

DB_PATH = os.getenv("BBS_DB_PATH", "./data/bbs.sqlite3")
BBS_PORT = int(os.getenv("BBS_PORT", "2323"))

ANSI_RESET  = "\x1b[0m"
ANSI_GREEN  = "\x1b[32m"
ANSI_CYAN   = "\x1b[36m"
ANSI_YELLOW = "\x1b[33m"

WELCOME = textwrap.dedent(f"""
{ANSI_CYAN}
==========================================
        WELCOME TO PY-BBS (Docker)
==========================================
{ANSI_RESET}
""")

MAIN_MENU = textwrap.dedent(f"""
{ANSI_GREEN}Main Menu{ANSI_RESET}
[1] Read messages
[2] Post a message
[3] Who's online
[4] Log out

Choice?> """)

###############################################################################
# Global in-memory session tracking (for /who)
###############################################################################

ACTIVE_USERS = set()
ACTIVE_LOCK = asyncio.Lock()

async def add_active_user(username):
    async with ACTIVE_LOCK:
        ACTIVE_USERS.add(username)

async def remove_active_user(username):
    async with ACTIVE_LOCK:
        if username in ACTIVE_USERS:
            ACTIVE_USERS.remove(username)

async def list_active_users():
    async with ACTIVE_LOCK:
        return list(ACTIVE_USERS)

###############################################################################
# Persistent storage layer (SQLite)
###############################################################################

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash BLOB NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        body TEXT NOT NULL,
        posted_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row  # (username, password_hash) or None

def create_user(username, password_plain):
    password_hash = bcrypt.hashpw(password_plain.encode("utf-8"), bcrypt.gensalt())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def list_messages(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT author, body, posted_at FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def post_message(author, body):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (author, body, posted_at) VALUES (?, ?, ?)",
        (author, body, datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

###############################################################################
# Telnet-ish I/O helpers
###############################################################################

async def send(writer, data: str):
    writer.write(data.encode("utf-8", errors="ignore"))
    await writer.drain()

async def recv_line(reader, timeout=300):
    """
    Read one line with a timeout (idle kick).
    Naive telnet cleanup: strip CR/LF.
    """
    try:
        data = await asyncio.wait_for(reader.readline(), timeout=timeout)
    except asyncio.TimeoutError:
        return None
    if not data:
        return None
    line = data.decode("utf-8", errors="ignore").strip("\r\n")
    return line

###############################################################################
# Session flow
###############################################################################

async def handle_login(reader, writer):
    await send(writer, WELCOME)

    # Username
    await send(writer, "Username: ")
    username = await recv_line(reader)
    if username is None:
        return None

    username = username.strip()

    row = get_user(username)
    if row is None:
        # new user flow
        await send(writer, f"New user '{username}'. Create password: ")
        pw = await recv_line(reader)
        if pw is None:
            return None
        try:
            create_user(username, pw)
            await send(writer, f"{ANSI_YELLOW}User created.{ANSI_RESET}\r\n")
        except Exception as e:
            await send(writer, f"Error creating user: {e}\r\n")
            return None
    else:
        # login flow
        stored_user, stored_hash = row
        await send(writer, "Password: ")
        pw = await recv_line(reader)
        if pw is None:
            return None
        if not bcrypt.checkpw(pw.encode("utf-8"), stored_hash):
            await send(writer, "Login failed.\r\n")
            return None

    return username

async def do_read_messages(writer):
    rows = list_messages(limit=10)
    if not rows:
        await send(writer, "\r\nNo messages yet.\r\n\r\n")
        return
    await send(writer, "\r\n--- Latest Messages ---\r\n")
    for author, body, ts in rows:
        await send(writer, f"[{ts}] {author}: {body}\r\n")
    await send(writer, "\r\n")

async def do_post_message(reader, writer, username):
    await send(writer, "\r\nEnter message (one line):\r\n> ")
    body = await recv_line(reader)
    if body is None:
        await send(writer, "\r\nTimed out.\r\n\r\n")
        return
    body = body.strip()
    if body:
        post_message(username, body)
        await send(writer, "Posted.\r\n\r\n")
    else:
        await send(writer, "Canceled.\r\n\r\n")

async def do_who(writer):
    current = await list_active_users()
    await send(writer, "\r\n--- Users Online ---\r\n")
    if not current:
        await send(writer, "(nobody)\r\n\r\n")
        return
    for u in current:
        await send(writer, f"- {u}\r\n")
    await send(writer, "\r\n")

async def session_task(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"[+] Connection from {addr}", flush=True)

    username = await handle_login(reader, writer)
    if username is None:
        await send(writer, "Goodbye.\r\n")
        writer.close()
        await writer.wait_closed()
        print(f"[-] {addr} login failed / disconnected", flush=True)
        return

    await add_active_user(username)
    await send(writer, f"\r\nWelcome, {username}!\r\n")

    try:
        while True:
            await send(writer, MAIN_MENU)
            choice = await recv_line(reader)
            if choice is None:
                await send(writer, "\r\nIdle timeout. Later.\r\n")
                break

            if choice == "1":
                await do_read_messages(writer)
            elif choice == "2":
                await do_post_message(reader, writer, username)
            elif choice == "3":
                await do_who(writer)
            elif choice == "4":
                await send(writer, "Logging out...\r\n")
                break
            else:
                await send(writer, "Invalid option.\r\n")
    finally:
        await remove_active_user(username)
        writer.close()
        await writer.wait_closed()
        print(f"[-] {addr} disconnected ({username})", flush=True)

###############################################################################
# Graceful shutdown handling
###############################################################################

stop_event = asyncio.Event()

def handle_sigterm():
    # Let asyncio loop exit cleanly
    print("[!] Received shutdown signal", flush=True)
    stop_event.set()

async def main():
    init_db()

    # Start TCP server
    server = await asyncio.start_server(
        session_task,
        host="0.0.0.0",
        port=BBS_PORT,
        start_serving=True
    )

    addr_list = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"[BBS] Listening on {addr_list}", flush=True)

    # Wait until we get SIGTERM or SIGINT
    await stop_event.wait()

    print("[BBS] Shutting down listener...", flush=True)
    server.close()
    await server.wait_closed()
    print("[BBS] Bye.", flush=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # Trap SIGTERM / SIGINT so Docker stop is graceful
    for sig in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(sig, handle_sigterm)

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()