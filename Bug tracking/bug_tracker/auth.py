from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from .db import get_db


bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = get_db().execute(
            "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("bugs.dashboard"))

        flash("Invalid username or password.")

    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))  
