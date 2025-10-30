from unittest.mock import patch


def test_google_auth_route(client, app):
    with app.app_context():
        app.config['GOOGLE_CLIENT_ID'] = 'test-client-id'
        app.config['GOOGLE_REDIRECT_URI'] = 'http://localhost/oauth/callback'
        response = client.get('/api/oauth/google/auth')
        assert response.status_code == 302
        assert 'accounts.google.com' in response.headers['Location']
        assert 'client_id=test-client-id' in response.headers['Location']
        assert 'redirect_uri=http%3A%2F%2Flocalhost%2Foauth%2Fcallback' in response.headers['Location']


def test_google_auth_route_config_error(client, app):
    with app.app_context():
        app.config['GOOGLE_CLIENT_ID'] = None
        app.config['GOOGLE_REDIRECT_URI'] = None
        response = client.get('/api/oauth/google/auth')
        assert response.status_code == 500
        assert response.get_json()['error'] == 'Google OAuth not configured'


def test_google_callback_missing_code(client, app):
    with app.app_context():
        response = client.get('/api/oauth/google/callback')
        assert response.status_code == 400
        assert response.get_json()['error'] == 'Missing authorization code'


def test_google_callback_token_exchange_error(client, app):
    with app.app_context():
        app.config['GOOGLE_CLIENT_ID'] = 'id'
        app.config['GOOGLE_CLIENT_SECRET'] = 'secret'
        app.config['GOOGLE_REDIRECT_URI'] = 'uri'
        with patch('services.user.app.controllers.oauth_controller.requests.post', side_effect=Exception('fail')):
            response = client.get('/api/oauth/google/callback?code=badcode')
            assert response.status_code == 500


def test_google_callback_invalid_token(client, app):
    with app.app_context():
        app.config['GOOGLE_CLIENT_ID'] = 'id'
        app.config['GOOGLE_CLIENT_SECRET'] = 'secret'
        app.config['GOOGLE_REDIRECT_URI'] = 'uri'
        with patch('services.user.app.controllers.oauth_controller.requests.post') as mock_post:
            mock_post.return_value.json.return_value = {'id_token': 'badtoken'}
            mock_post.return_value.raise_for_status = lambda: None
            with patch('services.user.app.controllers.oauth_controller.jwt.decode', side_effect=Exception('bad jwt')):
                response = client.get('/api/oauth/google/callback?code=code')
                assert response.status_code == 500
                assert 'Invalid token' in response.get_json()['error']


def test_google_callback_success_new_user(client, app, db_session, mocker):
    with app.app_context():
        app.config['GOOGLE_CLIENT_ID'] = 'id'
        app.config['GOOGLE_CLIENT_SECRET'] = 'secret'
        app.config['GOOGLE_REDIRECT_URI'] = 'uri'
        fake_tokens = {'id_token': 'goodtoken'}
        fake_userinfo = {
            'email': 'testuser@example.com',
            'sub': 'googleid123',
            'given_name': 'Test',
            'family_name': 'User',
            'picture': 'http://pic.url'
        }
        with patch('services.user.app.controllers.oauth_controller.requests.post') as mock_post:
            mock_post.return_value.json.return_value = fake_tokens
            mock_post.return_value.raise_for_status = lambda: None
            with patch('services.user.app.controllers.oauth_controller.jwt.decode', return_value=fake_userinfo):
                mock_login_user = mocker.patch('services.user.app.controllers.oauth_controller.login_user')
                response = client.get('/api/oauth/google/callback?code=code')
                assert response.status_code == 302
                assert response.headers['Location'].endswith('/student/dashboard')
                mock_login_user.assert_called_once()


def test_google_callback_success_existing_user(client, app, db_session, mocker):
    from services.user.app.models.user_model import User
    with app.app_context():
        app.config['GOOGLE_CLIENT_ID'] = 'id'
        app.config['GOOGLE_CLIENT_SECRET'] = 'secret'
        app.config['GOOGLE_REDIRECT_URI'] = 'uri'
        # Create user with matching social_provider_id
        import uuid
        unique_id = str(uuid.uuid4())
        user = User(email=f'exist_{unique_id}@example.com', name='Exist', surname='User', username=None, role='student', social_provider_id=unique_id, social_provider='Google')
        # Set additional attributes if needed
        db_session.add(user)
        db_session.commit()
        db_session.expire_all()
        fake_tokens = {'id_token': 'goodtoken'}
        fake_userinfo = {
            'email': f'exist_{unique_id}@example.com',
            'sub': unique_id,
            'given_name': 'Exist',
            'family_name': 'User',
            'picture': 'http://pic.url'
        }
        with patch('services.user.app.controllers.oauth_controller.requests.post') as mock_post:
            mock_post.return_value.json.return_value = fake_tokens
            mock_post.return_value.raise_for_status = lambda: None
            with patch('services.user.app.controllers.oauth_controller.jwt.decode', return_value=fake_userinfo):
                mock_login_user = mocker.patch('services.user.app.controllers.oauth_controller.login_user')
                response = client.get('/api/oauth/google/callback?code=code')
                assert response.status_code == 302
                assert response.headers['Location'].endswith('/student/dashboard')
                mock_login_user.assert_called_once()
