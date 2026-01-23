from flask import Blueprint, redirect, url_for
from flask_login import login_required

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
@login_required
def home():
    return redirect(url_for("tasks.week_view"))
