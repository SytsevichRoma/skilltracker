from flask import Blueprint
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
@login_required
def home():
    return f"Hello, {current_user.email} ✅"
