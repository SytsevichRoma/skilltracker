from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.goal import Goal

goals_bp = Blueprint("goals", __name__)

@goals_bp.get("/goals")
@login_required
def list_goals():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.id.desc()).all()
    return render_template("goals.html", goals=goals)

@goals_bp.route("/goals/create", methods=["GET", "POST"])
@login_required
def create_goal():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash("Вкажи назву цілі", "danger")
            return redirect(url_for("goals.create_goal"))

        goal = Goal(title=title, description=description, user_id=current_user.id)
        db.session.add(goal)
        db.session.commit()

        flash("Ціль створено ✅", "success")
        return redirect(url_for("goals.list_goals"))

    return render_template("goal_create.html")
