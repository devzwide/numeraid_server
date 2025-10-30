# User Service

This service provides user authentication, registration, OAuth integration, and profile management for the Numeraid platform.

## Features
- User registration and login
- OAuth login with Google
- User profile management
- Secure password hashing
- Role-based access (student, staff, admin)

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables as required in `config.py` (e.g., `SECRET_KEY`, `USER_DATABASE_URL`, OAuth credentials).
3. Run the service:
   ```bash
   python run.py
   ```

## Project Structure
- `app/` - Main application code (models, controllers, routes, forms, extensions)
- `tests/` - Unit and integration tests
- `documentation/` - Additional documentation

## Running Tests
From the `user_service` directory:
```bash
pytest tests
```

## License
See the main project [LICENSE](../../LICENSE).

