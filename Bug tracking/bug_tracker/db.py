import os
import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Developer', 'Tester', 'Project Manager'))
        );

        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL CHECK(priority IN ('Low', 'Medium', 'High', 'Critical')),
            status TEXT NOT NULL CHECK(status IN ('Open', 'In Progress', 'Resolved')) DEFAULT 'Open',
            assignee_id INTEGER,
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assignee_id) REFERENCES users (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bug_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bug_id) REFERENCES bugs (id)
        );
        """
    )

    _seed_users(db)
    _seed_sample_bugs(db)
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()


def _seed_users(db):
    users = [
        ("manager", "manager123", "Project Manager"),
        ("tester1", "tester123", "Tester"),
        ("dev1", "dev123", "Developer"),
    ]
    for username, password, role in users:
        existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing is None:
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role),
            )


def _seed_sample_bugs(db):
    existing_bug = db.execute("SELECT id FROM bugs LIMIT 1").fetchone()
    if existing_bug is not None:
        return

    creator = db.execute("SELECT id FROM users WHERE username = 'tester1'").fetchone()
    assignee = db.execute("SELECT id FROM users WHERE username = 'dev1'").fetchone()
    if creator is None or assignee is None:
        return

    sample_bugs = [
        (
            "Login page button overlap",
            "Login button overlaps footer on small screens.",
            "Medium",
            "Open",
            assignee["id"],
            creator["id"],
        ),
        (
            "Data export crash",
            "CSV export fails when issue description has commas.",
            "High",
            "In Progress",
            assignee["id"],
            creator["id"],
        ),
    ]
    for title, description, priority, status, assignee_id, created_by in sample_bugs:
        db.execute(
            """
            INSERT INTO bugs (title, description, priority, status, assignee_id, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, description, priority, status, assignee_id, created_by),
        )
