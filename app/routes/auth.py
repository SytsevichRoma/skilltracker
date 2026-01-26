from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask_babel import _
from sqlalchemy.exc import OperationalError
from app.extensions import db, bcrypt, login_manager
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except OperationalError:
        return None

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash(_("Please enter email and password"), "danger")
            return redirect(url_for("auth.register"))

        try:
            if User.query.filter_by(email=email).first():
                flash(_("This email is already registered"), "warning")
                return redirect(url_for("auth.register"))

            password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            user = User(email=email, password_hash=password_hash)

            db.session.add(user)
            db.session.commit()
        except OperationalError:
            db.session.rollback()
            flash(_("Database is not initialized. Please run migrations."), "danger")
            return render_template("register.html"), 503

        flash(_("Account created successfully ✅"), "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        try:
            user = User.query.filter_by(email=email).first()
        except OperationalError:
            db.session.rollback()
            flash(_("Database is not initialized. Please run migrations."), "danger")
            return render_template("login.html"), 503

        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            flash(_("Invalid email or password"), "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash(_("You are logged in ✅"), "success")
        return redirect(url_for("main.home"))

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash(_("You have logged out"), "info")
    return redirect(url_for("auth.login"))
