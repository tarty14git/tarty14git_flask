import json
import pytest
from app import create_app
from app.models import db, User, ReportConfig
from app.config import config

@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed test admin
            admin = User(username='testadmin', email='admin@test.com', is_admin=True)
            admin.set_password('Admin123!')
            db.session.add(admin)

            # Seed standard user
            user = User(username='testuser', email='user@test.com', is_admin=False)
            user.set_password('User123!')
            db.session.add(user)

            db.session.commit()
        yield client

def test_login_success(client):
    res = client.post('/login', json={'username': 'testadmin', 'password': 'Admin123!'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True

def test_login_invalid_password(client):
    res = client.post('/login', json={'username': 'testadmin', 'password': 'WrongPassword'})
    assert res.status_code == 401
    data = res.get_json()
    assert data['success'] is False

def test_account_registration(client):
    res = client.post('/register', json={
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'NewPassword123!',
        'full_name': 'New User'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True

def test_user_lock_unlock(client):
    # Login as admin
    res_admin = client.post('/login', json={'username': 'testadmin', 'password': 'Admin123!'})
    assert res_admin.status_code == 200

    # Get users to find testuser ID
    users_res = client.get('/users')
    users = users_res.get_json()['users']
    testuser_id = [u['id'] for u in users if u['username'] == 'testuser'][0]

    # Lock testuser
    res = client.post(f'/users/{testuser_id}/lock', json={'lock': True})
    assert res.status_code == 200
    assert res.get_json()['success'] is True

    # Attempt login with locked user
    client.post('/logout')
    res_login = client.post('/login', json={'username': 'testuser', 'password': 'User123!'})
    assert res_login.status_code == 403

def test_metadata_tables(client):
    res = client.get('/api/metadata/tables')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'users' in data['tables']

def test_report_generation(client):
    client.post('/login', json={'username': 'testadmin', 'password': 'Admin123!'})
    res = client.post('/api/reports/generate', json={
        'table_name': 'users',
        'fields': ['id', 'username', 'email']
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['data']) >= 2

def test_system_settings_update(client):
    client.post('/login', json={'username': 'testadmin', 'password': 'Admin123!'})
    res = client.post('/config/settings', json={
        'app.name': 'Updated Test Portal',
        '2fa.enabled': 'false'
    })
    assert res.status_code == 200
    assert res.get_json()['success'] is True
