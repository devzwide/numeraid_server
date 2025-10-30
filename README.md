# Numeraid

Numeraid is a modular backend server designed for scalable, service-oriented architectures. It is organized into multiple services, with a focus on user authentication, profile management, and OAuth integration.

## Project Structure

- `services/` - Contains all microservices and related configuration files.
  - `user/` - User service for authentication, profile, and OAuth.
    - `app/` - Main application code.
      - `controllers/` - Business logic for authentication, OAuth, and profile management.
      - `models/` - Data models (e.g., user model).
      - `routes/` - API route definitions.
      - `extensions.py` - App extensions (e.g., database, login manager).
      - `forms.py` - WTForms for user input.
    - `config.py` - Configuration for the user service.
    - `run.py` - Entry point to run the user service.
    - `Dockerfile` - Containerization for the user service.
    - `requirements.txt` - Python dependencies.
    - `tests/` - Unit and integration tests for the user service.
    - `README.md` - Documentation for the user service.
  - `docker-compose.yml` - Orchestrates multi-service setup.

## Getting Started

1. **Clone the repository**
2. **Install dependencies** (see each service's requirements.txt)
3. **Run services**
   - Using Docker Compose: `docker-compose up` from the `services/` directory
   - Or run each service individually (see their README.md files)
4. **Run tests**
   - Navigate to the `tests/` directory of each service and run `pytest`

## Features
- User authentication (register, login, logout)
- OAuth integration
- User profile management
- Modular, service-oriented design

## License
See [LICENSE](LICENSE) for details.
