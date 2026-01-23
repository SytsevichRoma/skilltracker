from datetime import date, timedelta, datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_babel import _

from app.extensions import db
from app.models.goal import Goal
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__)

TASK_TYPES = [
    ("must", _("Must")),
    ("goal", _("Goal")),
    ("dream", _("Dream")),
]

def _parse_date(value: str):
    """Parse YYYY-MM-DD -> date або None."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@tasks_bp.get("/week")
@login_required
def week_view():
    # старт тижня (понеділок)
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.id.desc()).all()
    goal_ids = [g.id for g in goals]

    tasks = []
    tasks_by_day = {start + timedelta(days=i): [] for i in range(7)}

    if goal_ids:
        tasks = (
            Task.query
            .filter(Task.goal_id.in_(goal_ids))
            .filter(Task.planned_for >= start, Task.planned_for <= end)
            .order_by(Task.planned_for.asc(), Task.id.desc())
            .all()
        )

        for t in tasks:
            if t.planned_for in tasks_by_day:
                tasks_by_day[t.planned_for].append(t)

    weekday_names = {
        0: _("Mon"),
        1: _("Tue"),
        2: _("Wed"),
        3: _("Thu"),
        4: _("Fri"),
        5: _("Sat"),
        6: _("Sun"),
    }

    days = [start + timedelta(days=i) for i in range(7)]

    return render_template(
        "week.html",
        days=days,
        today=today,
        goals=goals,
        tasks_by_day=tasks_by_day,
        weekday_names=weekday_names,
        task_types=TASK_TYPES,
    )


@tasks_bp.post("/tasks/create")
@login_required
def create_task():
    title = request.form.get("title", "").strip()
    goal_id = request.form.get("goal_id", "").strip()
    planned_for = _parse_date(request.form.get("planned_for", "").strip())
    task_type = request.form.get("task_type", "").strip() or None
    due_date = _parse_date(request.form.get("due_date", "").strip())

    if not title:
        flash(_("Title") + " ❌", "danger")
        return redirect(request.referrer or url_for("tasks.week_view"))

    # перевірка goal належить юзеру
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        flash(_("Goal") + " ❌", "danger")
        return redirect(request.referrer or url_for("tasks.week_view"))

    task = Task(
        title=title,
        goal_id=goal.id,
        planned_for=planned_for,
        task_type=task_type,
        due_date=due_date,
        is_done=False,
    )

    db.session.add(task)
    db.session.commit()

    flash(_("Task added ✅"), "success")
    return redirect(request.referrer or url_for("tasks.week_view"))
