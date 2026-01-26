from datetime import datetime
from flask_login import UserMixin
from ..extensions import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    is_pro = db.Column(db.Boolean, default=False, nullable=False)
    pro_until = db.Column(db.DateTime, nullable=True)
