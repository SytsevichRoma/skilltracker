from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import _

from app.extensions import db
from app.models.goal import Goal
from app.models.task import Task

goals_bp = Blueprint("goals", __name__)

@goals_bp.get("/goals")
@login_required
def list_goals():
    goals = (
        Goal.query
        .filter_by(user_id=current_user.id)
        .order_by(Goal.id.desc())
        .all()
    )
    return render_template("goals.html", goals=goals)

@goals_bp.route("/goals/create", methods=["GET", "POST"])
@login_required
def create_goal():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title:
            flash(_("Title") + " ❌", "danger")
            return redirect(url_for("goals.create_goal"))

        goal = Goal(title=title, description=description, user_id=current_user.id)
        db.session.add(goal)
        db.session.commit()

        flash(_("Goal created ✅"), "success")
        return redirect(url_for("goals.list_goals"))

    return render_template("goal_create.html")

@goals_bp.get("/goals/<int:goal_id>")
@login_required
def goal_detail(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    tasks = Task.query.filter_by(goal_id=goal.id).order_by(Task.id.desc()).all()
    return render_template("goal_detail.html", goal=goal, tasks=tasks)


@goals_bp.post("/goals/<int:goal_id>/delete")
@login_required
def delete_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()

    # ✅ видаляємо всі tasks цієї цілі (щоб не було foreign key проблем)
    Task.query.filter_by(goal_id=goal.id).delete()

    db.session.delete(goal)
    db.session.commit()

    flash(_("Goal deleted ✅"), "success")
    return redirect(url_for("goals.list_goals"))
