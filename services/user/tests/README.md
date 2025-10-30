# User Service Test Suite

This directory contains tests for the User Service, covering authentication, OAuth, and profile management.

## Structure
- `test_auth.py` - Tests for authentication routes (register, login, logout)
- `test_oauth.py` - Tests for Google OAuth integration
- `test_profile.py` - Tests for user profile endpoints
- `conftest.py` - Shared fixtures and test setup

## Running Tests
From the `numeraid_server/services/user/tests` directory, run:
```bash
pytest
```

## Writing Tests
- Use `pytest` for all tests.
- Fixtures for database and client setup are in `conftest.py`.
- Mock external services and forms as needed for isolation.

## Notes
- Ensure environment variables and test database are configured before running tests.
- All tests should pass before pushing changes.

