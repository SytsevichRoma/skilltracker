from datetime import datetime
from ..extensions import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    is_done = db.Column(db.Boolean, default=False, nullable=False)

    # тимчасово nullable=True (щоб SQLite дозволив ALTER TABLE)
    planned_for = db.Column(db.Date, nullable=True, index=True)

    # тимчасово nullable=True (бо SQLite не додасть NOT NULL без server_default)
    task_type = db.Column(db.String(20), nullable=True, index=True)

    due_date = db.Column(db.Date, nullable=True, index=True)

    goal_id = db.Column(db.Integer, db.ForeignKey("goal.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
