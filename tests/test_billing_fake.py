from app.extensions import db, bcrypt
from app.models.user import User
from app.models.payment import Payment


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


def test_fake_activate_sets_pro_and_payment(app, client):
    app.config["BILLING_PROVIDER"] = "fake"

    with app.app_context():
        _create_user()

    response = _login(client)
    assert response.status_code == 200

    resp = client.post("/billing/fake/activate", follow_redirects=True)
    assert resp.status_code == 200

    with app.app_context():
        user = User.query.first()
        assert user.is_pro is True
        assert user.pro_until is not None

        payment = Payment.query.filter_by(user_id=user.id).first()
        assert payment is not None
        assert payment.status == "paid"
        assert payment.provider == "fake"
