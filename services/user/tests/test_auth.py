import pytest

from unittest.mock import MagicMock, patch
from services.user.app.models.user_model import User

AUTH_BASE_URL = '/api/auth'


class MockRegisterForm:
    def __init__(self, data=None):
        self.data = data or {}
        self.email = MagicMock(data=self.data.get('email', ''))
        self.username = MagicMock(data=self.data.get('username', ''))
        self.name = MagicMock(data=self.data.get('name', ''))
        self.surname = MagicMock(data=self.data.get('surname', ''))
        self.password = MagicMock(data=self.data.get('password', ''))
        self.consent = MagicMock(data=self.data.get('consent', False))
        self.errors = {}

    def validate_on_submit(self):
        return True


class MockLoginForm:
    def __init__(self, data=None):
        self.data = data or {}
        self.email = MagicMock(data=self.data.get('email', ''))
        self.password = MagicMock(data=self.data.get('password', ''))
        self.remember = MagicMock(data=self.data.get('remember', False))
        self.errors = {}

    def validate_on_submit(self):
        return True


@pytest.fixture(autouse=True)
def mock_forms(mocker):
    mocker.patch('services.user.app.controllers.auth_controller.RegisterForm', MockRegisterForm)
    mocker.patch('services.user.app.controllers.auth_controller.LoginForm', MockLoginForm)


# --- Test Cases ---

@pytest.mark.parametrize('method', ['GET', 'PUT', 'DELETE'])
def test_auth_routes_wrong_method(client, method):
    """Test that all auth routes only accept POST requests (as defined in auth_router)."""

    # /register
    response_reg = client.open(f'{AUTH_BASE_URL}/register', method=method)
    assert response_reg.status_code == 405

    # /login
    response_login = client.open(f'{AUTH_BASE_URL}/login', method=method)
    assert response_login.status_code == 405

    # /logout (Note: Flask-Login will force a redirect/401 before hitting 405)
    # We check the status code the route allows, which is POST.
    # The actual controller is protected by @login_required, but the route itself is only POST.
    response_logout = client.open(f'{AUTH_BASE_URL}/logout', method=method)
    assert response_logout.status_code in [405, 401]  # 401 from @login_required, 405 from Flask-Blueprint


# --- Registration Tests ---

def test_register_route_success(client, db_session):
    """Test successful user registration."""

    # Setup mock form data that passes validation
    data = {
        'email': 'newuser@test.com',
        'username': 'newuser',
        'name': 'Test',
        'surname': 'User',
        'password': 'StrongPassword123',
        'consent': True
    }

    # Override the mock form instance with specific data for this test
    with patch('services.user.app.controllers.auth_controller.RegisterForm',
               lambda: MockRegisterForm(data=data)):
        response = client.post(f'{AUTH_BASE_URL}/register', json=data)

    assert response.status_code == 201
    assert response.get_json()['message'] == "User registered successfully."

    # Verify user creation in the database
    user = User.query.filter_by(email='newuser@test.com').first()
    assert user is not None
    assert user.username == 'newuser'

    # Clean up the session (handled by db_session fixture rollback)


def test_register_route_email_exists(client, db_session):
    """Test registration failure when email already exists."""

    # 1. Create a user manually
    existing_user = User(email='existing@test.com', username='exists', name='Test', surname='User', role='student')
    # Set additional attributes if needed
    existing_user.set_password('password')
    db_session.add(existing_user)
    db_session.commit()

    # 2. Setup mock form data for the duplicate user
    data = {'email': 'existing@test.com', 'username': 'new', 'password': 'p', 'consent': True}

    with patch('services.user.app.controllers.auth_controller.RegisterForm',
               lambda: MockRegisterForm(data=data)):
        response = client.post(f'{AUTH_BASE_URL}/register', json=data)

    assert response.status_code == 400
    assert response.get_json()['message'] == "Email already registered."


def test_register_route_form_validation_fail(client, mocker):
    """Test registration failure due to form validation errors."""

    # 1. Mock the form to fail validation and provide errors
    mock_form_instance = MockRegisterForm(data={'email': 'invalid'})
    mock_form_instance.validate_on_submit = MagicMock(return_value=False)
    mock_form_instance.errors = {'email': ['Not a valid email address.']}

    with patch('services.user.app.controllers.auth_controller.RegisterForm',
               lambda: mock_form_instance):
        response = client.post(f'{AUTH_BASE_URL}/register', json={'email': 'invalid'})

    assert response.status_code == 400
    assert response.get_json()['message'] == "Form validation failed."
    assert 'email' in response.get_json()['errors']


# --- Login Tests ---

# Fixture to set up a valid user for login/logout tests
@pytest.fixture
def setup_user(db_session, request):
    # Use a unique username/email per test function
    test_id = request.node.name
    email = f'{test_id}@test.com'
    username = f'{test_id}_user'
    user = User(email=email, username=username, name='Test', surname='User', role='student')
    user.set_password('testpassword')
    db_session.add(user)
    db_session.commit()
    return user


def test_login_route_success(client, setup_user, mocker):
    """Test successful user login."""

    # Mock the internal Flask-Login function
    mock_login_user = mocker.patch('services.user.app.controllers.auth_controller.login_user')

    # Use the same email as the created user
    data = {'email': setup_user.email, 'password': 'testpassword', 'remember': False}

    with patch('services.user.app.controllers.auth_controller.LoginForm',
               lambda: MockLoginForm(data=data)):
        response = client.post(f'{AUTH_BASE_URL}/login', json=data)

    assert response.status_code == 200
    assert response.get_json()['message'] == "Login successful."
    # Verify that the Flask-Login function was called
    mock_login_user.assert_called_once()


def test_login_route_invalid_credentials(client, setup_user):
    """Test login failure with incorrect password."""

    data = {'email': 'login@test.com', 'password': 'wrongpassword', 'remember': False}

    with patch('services.user.app.controllers.auth_controller.LoginForm',
               lambda: MockLoginForm(data=data)):
        response = client.post(f'{AUTH_BASE_URL}/login', json=data)

    assert response.status_code == 401
    assert response.get_json()['message'] == "Invalid email or password."


# --- Logout Tests ---

@patch('services.user.app.controllers.auth_controller.login_required', lambda func: func)
def test_logout_route_success(client, mocker):
    """Test successful user logout."""

    # Mock the internal Flask-Login function
    mock_logout_user = mocker.patch('services.user.app.controllers.auth_controller.logout_user')

    # Patch flask_login.utils._get_user to simulate an authenticated user
    mock_user = mocker.Mock()
    mock_user.is_authenticated = True
    mocker.patch('flask_login.utils._get_user', return_value=mock_user)

    response = client.post(f'{AUTH_BASE_URL}/logout')

    assert response.status_code == 200
    assert response.get_json()['message'] == "Logout successful."
    # Verify that the Flask-Login function was called
    mock_logout_user.assert_called_once()

# NOTE: Testing the real @login_required decorator requires more complex session
# setup. We simplify by mocking it out for the controller test, or relying on
# Flask-Login's default behavior (401/redirect) when not mocked for the route test.
