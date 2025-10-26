# BBS Testing Documentation

## Overview

The BBS project now includes a comprehensive test suite using **pytest** with proper organization and fixtures.

## Test Organization

### 📁 Test Structure

```
tests/
├── __init__.py                   # Package marker
├── conftest.py                   # Pytest fixtures and helpers
├── test_database.py              # ✅ Unit tests for database operations
├── test_docker_integration.py    # ✅ Integration tests with Docker
├── test_server.py                # 🔧 Server functionality (needs refinement)
├── test_performance.py           # 🔧 Performance tests (needs server fixes)
├── run_tests.py                  # 🎯 Test runner script
├── manual_test.py                # 🛠️ Manual testing utilities
└── legacy_*/                     # 📚 Original test files for reference
```

### 🧪 Test Categories

#### ✅ **Working Tests**

**Database Tests** (`test_database.py`)
- ✅ Database initialization
- ✅ User creation and authentication
- ✅ Message posting and retrieval
- ✅ Message ordering and limits
- ✅ Password hashing with bcrypt

**Docker Integration Tests** (`test_docker_integration.py`) 
- ✅ Connection to running Docker container
- ✅ Basic login flow verification
- 🔧 Message posting flow (needs timing adjustments)

#### 🔧 **Tests Needing Refinement**

**Server Tests** (`test_server.py`)
- ✅ Active user management (in-memory)
- 🔧 Full server integration (async timing issues)
- 🔧 Client-server communication protocol

**Performance Tests** (`test_performance.py`)
- 🔧 Concurrent connections
- 🔧 Database performance benchmarks
- 🔧 Connection cleanup verification

## 🏃 Running Tests

### Quick Commands

```bash
# Database tests (always work)
uv run pytest tests/test_database.py -v

# Docker tests (requires container running)
uv run pytest tests/test_docker_integration.py -v

# All working tests
uv run pytest tests/test_database.py tests/test_docker_integration.py -v

# Using test runner
uv run python tests/run_tests.py database
uv run python tests/run_tests.py docker
uv run python tests/run_tests.py all
```

### Test Runner Options

```bash
uv run python tests/run_tests.py <type> [options]

Types:
  all        - Run all available tests
  database   - Database unit tests only  
  docker     - Docker integration tests
  performance- Performance tests
  fast       - Quick unit tests

Options:
  -v         - Verbose output
  --coverage - Include coverage report
```

## 🔧 Current Status

### ✅ **What Works**
- **Database layer testing** - Complete and reliable
- **Basic Docker integration** - Container connectivity verified
- **Test organization** - Proper pytest structure with fixtures
- **Test automation** - Custom test runner with multiple options
- **Manual testing tools** - Database inspection and test data creation

### 🔧 **Known Issues**
1. **Async server fixtures** - Timing issues with async TCP server setup
2. **Client protocol handling** - Login flow timing in integration tests  
3. **Performance test dependencies** - Need stable server fixtures

### 🎯 **Recommendations**

1. **For reliable CI/CD**: Use database tests (`test_database.py`)
2. **For development**: Use Docker integration tests with running container
3. **For debugging**: Use manual test tools and legacy test files
4. **For production**: Focus on database tests + manual Docker verification

## 🛠️ Development Workflow

### Adding New Tests

1. **Database operations**: Add to `test_database.py`
2. **Integration features**: Add to `test_docker_integration.py`  
3. **Performance**: Add to `test_performance.py`
4. **Server internals**: Add to `test_server.py` (after fixing fixtures)

### Test-Driven Development

```bash
# 1. Write failing test
uv run pytest tests/test_database.py::TestDatabase::test_new_feature -v

# 2. Implement feature in bbs_server.py

# 3. Verify test passes
uv run python tests/run_tests.py database

# 4. Run full test suite
uv run python tests/run_tests.py all
```

### Manual Testing

```bash
# Check current database state
uv run python tests/manual_test.py

# Create test data for manual verification
uv run python tests/manual_test.py create-data

# Start server and test manually
docker compose up -d
telnet localhost 2323
```

## 📊 Test Coverage

Current focus areas:
- ✅ **Database operations** - Full coverage
- ✅ **User management** - Registration, login, password hashing
- ✅ **Message system** - Posting, retrieval, ordering
- 🔧 **Network protocol** - Async TCP handling needs work
- 🔧 **Concurrent users** - Multi-client testing in progress

## 🚀 Future Improvements

1. **Fix async server fixtures** for complete integration testing
2. **Add WebSocket support** and corresponding tests
3. **Implement rate limiting** with appropriate test coverage
4. **Add security tests** for SQL injection, input validation
5. **Performance benchmarking** with proper async handling
6. **CI/CD integration** with GitHub Actions