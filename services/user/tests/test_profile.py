import pytest
from services.user.app.models.user_model import User
from services.user.app.extensions import db

def create_test_user():
    user = User(
        email='profile@test.com',
        username='testuser',
        password_hash='testhash',
        name='Test',
        surname='User',
        role='student',
        profile_picture_url='http://example.com/pic.png'
    )
    user.is_active = True
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_user(db_session):
    user = create_test_user()
    yield user
    db.session.delete(user)
    db.session.commit()

@pytest.fixture
def authenticated_client(client, test_user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.user_id)
    return client

def test_get_profile_authenticated(authenticated_client, test_user):
    response = authenticated_client.get('/api/profile/me')
    assert response.status_code == 200
    data = response.get_json()
    assert data['email'] == test_user.email
    assert data['username'] == test_user.username
    assert data['name'] == test_user.name
    assert data['surname'] == test_user.surname
    assert data['role'] == test_user.role
    assert data['profile_picture_url'] == test_user.profile_picture_url

def test_get_profile_unauthenticated(client):
    response = client.get('/api/profile/me')
    assert response.status_code == 401

def test_update_profile_authenticated(authenticated_client, test_user):
    update_data = {
        'name': 'Updated',
        'surname': 'User',
        'username': 'updateduser'
    }
    response = authenticated_client.put('/api/profile/me', json=update_data)
    assert response.status_code == 200
    db.session.refresh(test_user)
    assert test_user.name == 'Updated'
    assert test_user.username == 'updateduser'

def test_update_profile_unauthenticated(client):
    response = client.put('/api/profile/me', json={'name': 'X'})
    assert response.status_code == 401
