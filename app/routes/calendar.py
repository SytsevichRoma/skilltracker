from datetime import date
from calendar import monthrange
from collections import defaultdict

from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from app.models.goal import Goal
from app.models.task import Task

calendar_bp = Blueprint("calendar", __name__)

@calendar_bp.get("/calendar")
@login_required
def month_view():
    # ?ym=2026-01 (за замовчуванням поточний місяць)
    ym = request.args.get("ym")
    if ym:
        y, m = ym.split("-")
        year, month = int(y), int(m)
    else:
        today = date.today()
        year, month = today.year, today.month

    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    goals = Goal.query.filter_by(user_id=current_user.id).all()
    goal_ids = [g.id for g in goals]

    tasks = []
    tasks_by_day = defaultdict(list)

    if goal_ids:
        tasks = (
            Task.query
            .filter(Task.goal_id.in_(goal_ids))
            .filter(Task.planned_for >= first_day, Task.planned_for <= last_day)
            .order_by(Task.planned_for.asc(), Task.id.desc())
            .all()
        )
        for t in tasks:
            if t.planned_for:
                tasks_by_day[t.planned_for].append(t)

    # календарна сітка (понеділок-початок)
    start_weekday = first_day.weekday()  # Mon=0
    days_in_month = last_day.day

    cells = []
    for _ in range(start_weekday):
        cells.append(None)
    for d in range(1, days_in_month + 1):
        cells.append(date(year, month, d))
    while len(cells) % 7 != 0:
        cells.append(None)

    # prev/next
    prev_year, prev_month = year, month - 1
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_year, next_month = year, month + 1
    if next_month == 13:
        next_month = 1
        next_year += 1

    return render_template(
        "calendar.html",
        year=year,
        month=month,
        first_day=first_day,
        cells=cells,
        tasks_by_day=tasks_by_day,
        prev_ym=f"{prev_year:04d}-{prev_month:02d}",
        next_ym=f"{next_year:04d}-{next_month:02d}",
        today=date.today(),
    )
