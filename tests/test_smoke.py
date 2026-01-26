from app.extensions import db, bcrypt
from app.models.user import User


def _create_user(email="test@example.com", password="password123"):
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return user


def _login(client, email="test@example.com", password="password123"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_authenticated_pages_smoke(app, client):
    with app.app_context():
        _create_user()

    response = _login(client)
    assert response.status_code == 200

    for path in ("/week", "/goals", "/calendar", "/stats"):
        resp = client.get(path)
        assert resp.status_code == 200
