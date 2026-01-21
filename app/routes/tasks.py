from datetime import date, timedelta
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user

from app.extensions import db
from app.models.goal import Goal
from app.models.task import Task

tasks_bp = Blueprint("tasks", __name__)

TASK_TYPES = [
    ("DREAM", "Мрії"),
    ("GOAL", "Мети"),
    ("MUST", "Обов'язкові"),
]

TYPE_ORDER = {"DREAM": 0, "GOAL": 1, "MUST": 2}


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        y, m, d = value.split("-")
        return date(int(y), int(m), int(d))
    except Exception:
        return None


def _type_label(code: str | None) -> str:
    code = (code or "MUST").upper()
    return "Мрії" if code == "DREAM" else ("Мети" if code == "GOAL" else "Обов'язкові")


@tasks_bp.get("/week")
@login_required
def week_view():
    today = date.today()
    days = [today + timedelta(days=i) for i in range(7)]

    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.id.desc()).all()
    goal_ids = [g.id for g in goals]

    tasks = []
    if goal_ids:
        tasks = (
            Task.query
            .filter(Task.goal_id.in_(goal_ids))
            .filter(Task.planned_for >= days[0])
            .filter(Task.planned_for <= days[-1])
            .all()
        )

    # структура:
    # tasks_by_day[d] = {
    #   "groups": {"DREAM":[...], "GOAL":[...], "MUST":[...]},
    #   "total": int, "done": int, "percent": int
    # }
    tasks_by_day = {}
    for d in days:
        tasks_by_day[d] = {
            "groups": {"DREAM": [], "GOAL": [], "MUST": []},
            "total": 0,
            "done": 0,
            "percent": 0,
        }

    # розкидали по днях і групах
    for t in tasks:
        pf = t.planned_for
        if pf not in tasks_by_day:
            continue
        t.task_type = (t.task_type or "MUST").upper()

        code = t.task_type if t.task_type in ("DREAM", "GOAL", "MUST") else "MUST"
        tasks_by_day[pf]["groups"][code].append(t)
        tasks_by_day[pf]["total"] += 1
        if t.is_done:
            tasks_by_day[pf]["done"] += 1

    # сортування всередині кожної групи: спочатку невиконані, потім виконані, далі за id desc
    for d in days:
        for code in ("DREAM", "GOAL", "MUST"):
            tasks_by_day[d]["groups"][code].sort(key=lambda x: (x.is_done, -x.id))

        total = tasks_by_day[d]["total"]
        done = tasks_by_day[d]["done"]
        tasks_by_day[d]["percent"] = int((done / total) * 100) if total else 0

    return render_template(
        "week.html",
        days=days,
        tasks_by_day=tasks_by_day,
        goals=goals,
        task_types=TASK_TYPES,
        type_label=_type_label,
    )


@tasks_bp.post("/tasks/create")
@login_required
def create_task():
    goal_id = request.form.get("goal_id", type=int)
    title = request.form.get("title", "").strip()
    planned_for = _parse_date(request.form.get("planned_for"))
    task_type = (request.form.get("task_type") or "MUST").strip().upper()
    due_date = _parse_date(request.form.get("due_date"))

    if not goal_id or not title or not planned_for:
        flash("Некоректні дані (goal, title, planned_for)", "danger")
        return redirect(url_for("tasks.week_view"))

    allowed = {k for k, _ in TASK_TYPES}
    if task_type not in allowed:
        task_type = "MUST"

    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()

    task = Task(
        title=title,
        goal_id=goal.id,
        planned_for=planned_for,
        task_type=task_type,
        due_date=due_date,
    )
    db.session.add(task)
    db.session.commit()

    flash("Задача додана ✅", "success")
    return redirect(url_for("tasks.week_view"))


@tasks_bp.post("/tasks/<int:task_id>/toggle")
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    Goal.query.filter_by(id=task.goal_id, user_id=current_user.id).first_or_404()

    task.is_done = not task.is_done
    db.session.commit()

    return redirect(url_for("tasks.week_view"))


@tasks_bp.post("/tasks/<int:task_id>/delete")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    Goal.query.filter_by(id=task.goal_id, user_id=current_user.id).first_or_404()

    db.session.delete(task)
    db.session.commit()

    flash("Задачу видалено 🗑️", "info")
    return redirect(url_for("tasks.week_view"))
