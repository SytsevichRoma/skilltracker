from app.extensions import db, bcrypt
from app.models.user import User
from app.models.goal import Goal
from app.models.task import Task


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


def test_toggle_task_updates_completed_at(app, client):
    with app.app_context():
        user = _create_user()
        goal = Goal(title="Goal", description=None, user_id=user.id)
        db.session.add(goal)
        db.session.commit()

        task = Task(title="Task", goal_id=goal.id, is_done=False)
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = _login(client)
    assert response.status_code == 200

    resp = client.post(f"/tasks/{task_id}/toggle")
    assert resp.status_code == 302

    with app.app_context():
        db.session.expire_all()
        task = db.session.get(Task, task_id)
        assert task.is_done is True
        assert task.completed_at is not None

    resp = client.post(f"/tasks/{task_id}/toggle")
    assert resp.status_code == 302

    with app.app_context():
        db.session.expire_all()
        task = db.session.get(Task, task_id)
        assert task.is_done is False
        assert task.completed_at is None
