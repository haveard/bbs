# Telnet-style BBS (Bulletin Board System)

A modern implementation of a classic telnet-style BBS server built with Python 3.11, asyncio, and SQLite.

## Features

- 🔌 **Telnet-style interface** - Connect via telnet or any TCP client
- 👥 **Multi-user support** - Multiple concurrent users
- 🔐 **User authentication** - Automatic registration and login
- 💬 **Message board** - Post and read messages
- 👀 **Who's online** - See active users
- 💾 **SQLite persistence** - User accounts and messages persist across restarts
- 🐳 **Docker ready** - Easily containerized and deployable
- ⚡ **Async architecture** - Built on asyncio for high performance

## Quick Start

### Using Docker (Recommended)

1. **Build and start the BBS:**
   ```bash
   docker compose up -d
   ```

2. **Connect via telnet:**
   ```bash
   telnet localhost 2323
   ```

3. **Stop the BBS:**
   ```bash
   docker compose down
   ```

### Using UV (Development)

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Run the server:**
   ```bash
   uv run python main.py
   ```

3. **Connect from another terminal:**
   ```bash
   telnet localhost 2323
   ```

## Usage

Once connected, you'll see a welcome screen and be prompted for:

1. **Username** - Enter a username (new users are automatically registered)
2. **Password** - Set a password for new users, or enter existing password

### Main Menu Options

- **[1] Read messages** - View the latest messages
- **[2] Post a message** - Post a new message to the board
- **[3] Who's online** - See who's currently connected
- **[4] Log out** - Disconnect from the BBS

## Configuration

Environment variables:

- `BBS_PORT` - Port to listen on (default: 2323)
- `BBS_DB_PATH` - Path to SQLite database (default: `./data/bbs.sqlite3`)

## Project Structure

```
bbs/
├── main.py            # Application entry point (CLI interface)
├── bbs_server.py      # BBS server implementation  
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container build instructions
├── docker-compose.yml # Container orchestration
├── data/              # SQLite database storage
├── tests/             # Test suite
├── scripts/           # Utility scripts
├── docs/              # Documentation
├── AGENT.md          # Instructions for AI agents
└── README.md         # This file
```

## Development

This project uses **UV** for Python environment management. **IMPORTANT**: See `AGENT.md` for detailed instructions for AI agents working on this project, including mandatory testing requirements and file organization rules.

### ⚠️ For Agents and Developers

**REQUIRED READING**: [AGENT.md](AGENT.md) - Contains critical development guidelines including:
- Mandatory testing after every change
- File organization rules (scripts/, docs/, tests/)
- Testing workflow requirements
- Development environment setup

### Testing

The project includes a comprehensive test suite using **pytest**:

#### Test Structure

```
tests/
├── test_database.py          # Database operation tests
├── test_docker_integration.py # Docker container tests  
├── test_server.py            # Server functionality tests
├── test_performance.py       # Performance and stress tests
├── conftest.py              # Pytest fixtures and helpers
├── run_tests.py             # Test runner script
└── legacy_*                 # Legacy test files for reference
```

#### Running Tests

**Quick test run:**
```bash
uv run pytest tests/test_database.py -v
```

**All working tests:**
```bash
uv run pytest tests/test_database.py tests/test_docker_integration.py -v
```

**Using the test runner:**
```bash
# Run all tests
uv run python tests/run_tests.py all

# Run only database tests
uv run python tests/run_tests.py database

# Run Docker integration tests (requires running container)
uv run python tests/run_tests.py docker

# Run with coverage
uv run python tests/run_tests.py all --coverage
```

#### Test Requirements

- **Database tests**: No special requirements
- **Docker tests**: Require BBS container running on port 2323
- **Server tests**: Currently being refined for async testing

#### Manual Testing

For manual testing and database inspection:

```bash
# Check database contents
uv run python tests/manual_test.py

# Create test data
uv run python tests/manual_test.py create-data
```

## Deployment

### AWS EC2 Deployment

1. Launch an EC2 instance (t3.micro is sufficient)
2. Install Docker and Docker Compose
3. Copy project files to the instance
4. Run `docker compose up -d`
5. Configure security group to allow inbound TCP 2323
6. Connect via `telnet <ec2-public-ip> 2323`

### Security Considerations

For production deployment, consider:

- Rate limiting for connections and messages
- Maximum message length limits
- IP-based ban system for failed logins
- SSL/TLS termination via reverse proxy
- Regular database backups

## Technology Stack

- **Python 3.11+** - Modern Python with UV package management
- **asyncio** - Asynchronous networking
- **SQLite** - Embedded database
- **bcrypt** - Password hashing
- **Docker** - Containerization

## License

This is an example project for educational purposes.