from datetime import date, timedelta

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models.goal import Goal
from app.models.task import Task

stats_bp = Blueprint("stats", __name__)


def _completion_date(task: Task):
    if task.completed_at:
        return task.completed_at.date()
    if task.planned_for:
        return task.planned_for
    if task.created_at:
        return task.created_at.date()
    return None


def _heat_level(count: int) -> int:
    if count <= 0:
        return 0
    if count == 1:
        return 1
    if count <= 3:
        return 2
    if count <= 6:
        return 3
    return 4


@stats_bp.get("/stats")
@login_required
def stats_view():
    today = date.today()
    start_90 = today - timedelta(days=89)
    start_30 = today - timedelta(days=29)
    start_week = today - timedelta(days=today.weekday())
    start_month = today.replace(day=1)

    tasks = (
        Task.query
        .join(Goal)
        .filter(Goal.user_id == current_user.id, Task.is_done.is_(True))
        .all()
    )

    date_counts = {}
    goal_counts_30 = {}

    for task in tasks:
        comp_date = _completion_date(task)
        if not comp_date:
            continue

        date_counts[comp_date] = date_counts.get(comp_date, 0) + 1

        if comp_date >= start_30:
            goal_counts_30[task.goal_id] = goal_counts_30.get(task.goal_id, 0) + 1

    completed_today = date_counts.get(today, 0)
    completed_week = sum(
        count for d, count in date_counts.items()
        if start_week <= d <= today
    )
    completed_month = sum(
        count for d, count in date_counts.items()
        if start_month <= d <= today
    )

    streak = 0
    cursor = today
    while date_counts.get(cursor, 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)

    heat_levels = {}
    heat_counts = {}
    for i in range(90):
        day = start_90 + timedelta(days=i)
        count = date_counts.get(day, 0)
        heat_counts[day] = count
        heat_levels[day] = _heat_level(count)

    start_calendar = start_90 - timedelta(days=start_90.weekday())
    weeks = []
    current = start_calendar
    while current <= today:
        week = []
        for i in range(7):
            day = current + timedelta(days=i)
            if day < start_90 or day > today:
                week.append(None)
            else:
                week.append(day)
        weeks.append(week)
        current += timedelta(days=7)

    goals = Goal.query.filter_by(user_id=current_user.id).all()
    goal_map = {g.id: g for g in goals}

    top_goals = [
        (goal_map[goal_id], count)
        for goal_id, count in goal_counts_30.items()
        if goal_id in goal_map
    ]
    top_goals.sort(key=lambda item: item[1], reverse=True)

    return render_template(
        "stats.html",
        completed_today=completed_today,
        completed_week=completed_week,
        completed_month=completed_month,
        streak=streak,
        weeks=weeks,
        heat_levels=heat_levels,
        heat_counts=heat_counts,
        top_goals=top_goals,
    )
