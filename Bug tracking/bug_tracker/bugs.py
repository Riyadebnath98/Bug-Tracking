from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from .auth import login_required
from .db import get_db


bp = Blueprint("bugs", __name__)

ALLOWED_STATUSES = {"Open", "In Progress", "Resolved"}
ALLOWED_PRIORITIES = {"Low", "Medium", "High", "Critical"}


@bp.route("/")
@login_required
def dashboard():
    db = get_db()

    query = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    assignee = request.args.get("assignee", "").strip() 

    sql = """
        SELECT
            b.id, b.title, b.description, b.priority, b.status, b.created_at, b.updated_at,
            cu.username AS created_by_name,
            au.username AS assignee_name
        FROM bugs b
        JOIN users cu ON b.created_by = cu.id
        LEFT JOIN users au ON b.assignee_id = au.id
        WHERE 1=1
    """
    params = []
    if query:
        sql += " AND (b.title LIKE ? OR b.description LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    if status in ALLOWED_STATUSES:
        sql += " AND b.status = ?"
        params.append(status)
    if priority in ALLOWED_PRIORITIES:
        sql += " AND b.priority = ?"
        params.append(priority)
    if assignee:
        sql += " AND au.username = ?"
        params.append(assignee)
    sql += " ORDER BY b.id DESC"

    bugs = db.execute(sql, params).fetchall()
    users = db.execute("SELECT id, username, role FROM users ORDER BY username ASC").fetchall()
    notifications = db.execute(
        """
        SELECT al.message, al.created_at, b.id AS bug_id
        FROM activity_log al
        JOIN bugs b ON b.id = al.bug_id
        ORDER BY al.id DESC
        LIMIT 8
        """
    ).fetchall()

    return render_template(
        "dashboard.html",
        bugs=bugs,
        users=users,
        notifications=notifications,
        filters={"q": query, "status": status, "priority": priority, "assignee": assignee},
    )


@bp.route("/bugs/create", methods=["POST"])
@login_required
def create_bug():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "").strip()
    assignee_id = request.form.get("assignee_id", "").strip()

    if not title or not description or priority not in ALLOWED_PRIORITIES:
        flash("Please provide title, description, and valid priority.")
        return redirect(url_for("bugs.dashboard"))

    assignee_value = int(assignee_id) if assignee_id.isdigit() else None
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO bugs (title, description, priority, status, assignee_id, created_by, updated_at)
        VALUES (?, ?, ?, 'Open', ?, ?, CURRENT_TIMESTAMP)
        """,
        (title, description, priority, assignee_value, session["user_id"]),
    )
    bug_id = cursor.lastrowid
    db.execute(
        "INSERT INTO activity_log (bug_id, message) VALUES (?, ?)",
        (bug_id, f"{session['username']} created this bug with status Open."),
    )
    db.commit()
    flash("Bug created successfully.")
    return redirect(url_for("bugs.dashboard"))


@bp.route("/bugs/<int:bug_id>/edit", methods=["GET", "POST"])
@login_required
def edit_bug(bug_id):
    db = get_db()
    bug = _get_bug_or_redirect(db, bug_id)
    if bug is None:
        return redirect(url_for("bugs.dashboard"))

    users = db.execute("SELECT id, username FROM users ORDER BY username ASC").fetchall()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "").strip()
        assignee_id = request.form.get("assignee_id", "").strip()

        if not title or not description or priority not in ALLOWED_PRIORITIES:
            flash("Please provide title, description, and valid priority.")
            return render_template("edit_bug.html", bug=bug, users=users)

        assignee_value = int(assignee_id) if assignee_id.isdigit() else None
        db.execute(
            """
            UPDATE bugs
            SET title = ?, description = ?, priority = ?, assignee_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (title, description, priority, assignee_value, bug_id),
        )
        db.execute(
            "INSERT INTO activity_log (bug_id, message) VALUES (?, ?)",
            (bug_id, f"{session['username']} updated bug details."),
        )
        db.commit()
        flash("Bug updated successfully.")
        return redirect(url_for("bugs.dashboard"))

    return render_template("edit_bug.html", bug=bug, users=users)


@bp.route("/bugs/<int:bug_id>/status", methods=["POST"])
@login_required
def update_bug_status(bug_id):
    new_status = request.form.get("status", "").strip()
    if new_status not in ALLOWED_STATUSES:
        flash("Invalid status.")
        return redirect(url_for("bugs.dashboard"))

    db = get_db()
    bug = _get_bug_or_redirect(db, bug_id)
    if bug is None:
        return redirect(url_for("bugs.dashboard"))

    db.execute(
        "UPDATE bugs SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_status, bug_id),
    )
    db.execute( 
        "INSERT INTO activity_log (bug_id, message) VALUES (?, ?)",
        (bug_id, f"{session['username']} changed status to {new_status}."),
    )
    db.commit()
    flash("Bug status updated.")
    return redirect(url_for("bugs.dashboard"))


@bp.route("/bugs/<int:bug_id>/delete", methods=["POST"])
@login_required
def delete_bug(bug_id):
    db = get_db()
    bug = _get_bug_or_redirect(db, bug_id)
    if bug is None:
        return redirect(url_for("bugs.dashboard"))

    db.execute("DELETE FROM activity_log WHERE bug_id = ?", (bug_id,))
    db.execute("DELETE FROM bugs WHERE id = ?", (bug_id,))
    db.commit()
    flash("Bug deleted successfully.")
    return redirect(url_for("bugs.dashboard"))


def _get_bug_or_redirect(db, bug_id):
    bug = db.execute(
        """
        SELECT id, title, description, priority, status, assignee_id
        FROM bugs
        WHERE id = ?
        """,
        (bug_id,),
    ).fetchone()
    if bug is None:
        flash("Bug not found.")
        return None
    return bug
