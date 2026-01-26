from datetime import datetime

from app.extensions import db


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    order_id = db.Column(db.String(64), nullable=False, unique=True, index=True)
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(8), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    provider = db.Column(db.String(16), nullable=False, default="fondy", index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
