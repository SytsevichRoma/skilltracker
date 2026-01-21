from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models.goal import Goal
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.post("/tasks/create")
@login_required
def create_task():
    goal_id = request.form.get("goal_id", type=int)
    title = request.form.get("title", "").strip()

    if not goal_id or not title:
        flash("Некоректні дані", "danger")
        return redirect(url_for("goals.list_goals"))

    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()

    task = Task(title=title, goal_id=goal.id)
    db.session.add(task)
    db.session.commit()

    flash("Задача додана ✅", "success")
    return redirect(url_for("goals.goal_detail", goal_id=goal.id))


@tasks_bp.post("/tasks/<int:task_id>/toggle")
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    goal = Goal.query.filter_by(id=task.goal_id, user_id=current_user.id).first_or_404()

    task.is_done = not task.is_done
    db.session.commit()

    return redirect(url_for("goals.goal_detail", goal_id=goal.id))


@tasks_bp.post("/tasks/<int:task_id>/delete")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    goal = Goal.query.filter_by(id=task.goal_id, user_id=current_user.id).first_or_404()

    db.session.delete(task)
    db.session.commit()

    flash("Задачу видалено 🗑️", "info")
    return redirect(url_for("goals.goal_detail", goal_id=goal.id))
