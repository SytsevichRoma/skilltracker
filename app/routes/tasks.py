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

ALLOWED_TYPES = {k for k, _ in TASK_TYPES}


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


def _normalize_type(code: str | None) -> str:
    code = (code or "MUST").strip().upper()
    return code if code in ALLOWED_TYPES else "MUST"


def _user_goals():
    return Goal.query.filter_by(user_id=current_user.id).order_by(Goal.id.desc()).all()


def _ensure_task_owner(task: Task) -> Goal:
    # task має належати goal поточного користувача
    return Goal.query.filter_by(id=task.goal_id, user_id=current_user.id).first_or_404()


@tasks_bp.get("/week")
@login_required
def week_view():
    today = date.today()
    days = [today + timedelta(days=i) for i in range(7)]

    goals = _user_goals()
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

    tasks_by_day = {}
    for d in days:
        tasks_by_day[d] = {
            "groups": {"DREAM": [], "GOAL": [], "MUST": []},
            "total": 0,
            "done": 0,
            "percent": 0,
        }

    for t in tasks:
        pf = t.planned_for
        if pf not in tasks_by_day:
            continue
        t.task_type = _normalize_type(t.task_type)

        tasks_by_day[pf]["groups"][t.task_type].append(t)
        tasks_by_day[pf]["total"] += 1
        if t.is_done:
            tasks_by_day[pf]["done"] += 1

    # сортування: спочатку not done, потім done, за id desc
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
    task_type = _normalize_type(request.form.get("task_type"))
    due_date = _parse_date(request.form.get("due_date"))

    if not goal_id or not title or not planned_for:
        flash("Некоректні дані (goal, title, planned_for)", "danger")
        return redirect(url_for("tasks.week_view"))

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
    _ensure_task_owner(task)

    task.is_done = not task.is_done
    db.session.commit()
    return redirect(url_for("tasks.week_view"))


@tasks_bp.post("/tasks/<int:task_id>/delete")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    _ensure_task_owner(task)

    db.session.delete(task)
    db.session.commit()

    flash("Задачу видалено 🗑️", "info")
    return redirect(url_for("tasks.week_view"))


# ✅ 1) MOVE: перенести задачу на інший день
@tasks_bp.post("/tasks/<int:task_id>/move")
@login_required
def move_task(task_id):
    task = Task.query.get_or_404(task_id)
    _ensure_task_owner(task)

    new_date = _parse_date(request.form.get("planned_for"))
    if not new_date:
        flash("Некоректна дата", "danger")
        return redirect(url_for("tasks.week_view"))

    task.planned_for = new_date
    db.session.commit()
    return redirect(url_for("tasks.week_view"))


# ✅ 2) EDIT: редагування задачі
@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    _ensure_task_owner(task)

    goals = _user_goals()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        goal_id = request.form.get("goal_id", type=int)
        planned_for = _parse_date(request.form.get("planned_for"))
        task_type = _normalize_type(request.form.get("task_type"))
        due_date = _parse_date(request.form.get("due_date"))

        if not title or not goal_id or not planned_for:
            flash("Заповни title, goal, planned_for", "danger")
            return redirect(url_for("tasks.edit_task", task_id=task.id))

        # goal має належати користувачу
        goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()

        task.title = title
        task.goal_id = goal.id
        task.planned_for = planned_for
        task.task_type = task_type
        task.due_date = due_date

        db.session.commit()
        flash("Задачу оновлено ✅", "success")
        return redirect(url_for("tasks.week_view"))

    return render_template("task_edit.html", task=task, goals=goals, task_types=TASK_TYPES)


# ✅ 3) COPY DAY → TOMORROW
@tasks_bp.post("/week/<string:day_str>/copy_to_tomorrow")
@login_required
def copy_day_to_tomorrow(day_str):
    day = _parse_date(day_str)
    if not day:
        flash("Некоректний день", "danger")
        return redirect(url_for("tasks.week_view"))

    tomorrow = day + timedelta(days=1)

    goals = _user_goals()
    goal_ids = [g.id for g in goals]
    if not goal_ids:
        flash("Нема goals", "danger")
        return redirect(url_for("tasks.week_view"))

    day_tasks = (
        Task.query
        .filter(Task.goal_id.in_(goal_ids))
        .filter(Task.planned_for == day)
        .all()
    )

    for t in day_tasks:
        new_task = Task(
            title=t.title,
            is_done=False,
            planned_for=tomorrow,
            task_type=_normalize_type(t.task_type),
            due_date=t.due_date,
            goal_id=t.goal_id,
        )
        db.session.add(new_task)

    db.session.commit()
    flash("План скопійовано на завтра ✅", "success")
    return redirect(url_for("tasks.week_view"))


# ✅ 4) MARK ALL DONE (на день)
@tasks_bp.post("/week/<string:day_str>/mark_all_done")
@login_required
def mark_all_done(day_str):
    day = _parse_date(day_str)
    if not day:
        flash("Некоректний день", "danger")
        return redirect(url_for("tasks.week_view"))

    goals = _user_goals()
    goal_ids = [g.id for g in goals]
    if goal_ids:
        (
            Task.query
            .filter(Task.goal_id.in_(goal_ids))
            .filter(Task.planned_for == day)
            .update({Task.is_done: True})
        )
        db.session.commit()

    flash("Всі задачі дня позначено як Done ✅", "success")
    return redirect(url_for("tasks.week_view"))


# ✅ 5) CLEAR DAY (видалити всі задачі дня)
@tasks_bp.post("/week/<string:day_str>/clear_day")
@login_required
def clear_day(day_str):
    day = _parse_date(day_str)
    if not day:
        flash("Некоректний день", "danger")
        return redirect(url_for("tasks.week_view"))

    goals = _user_goals()
    goal_ids = [g.id for g in goals]
    if goal_ids:
        (
            Task.query
            .filter(Task.goal_id.in_(goal_ids))
            .filter(Task.planned_for == day)
            .delete(synchronize_session=False)
        )
        db.session.commit()

    flash("День очищено 🗑️", "info")
    return redirect(url_for("tasks.week_view"))
