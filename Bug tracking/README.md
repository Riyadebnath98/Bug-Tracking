# Bug Tracking System

This project is built with Flask + SQLite and follows the software engineering mini-project requirements.

## Completed Requirements

- Objective implemented: log, track, and manage software bugs
- User roles implemented: `Developer`, `Tester`, `Project Manager`
- SQLite schema includes: `id`, `description`, `priority`, `status`, `assignee`, `created_by`
- Full CRUD for bugs: Create, Read, Update (details + status), Delete
- Search and filter available by text, status, priority, and assignee
- Notifications implemented through `activity_log` for status/detail updates
- Sample test data automatically seeded on first run
- Local deployment supported on localhost

## Default Users

- `manager / manager123` (Project Manager)
- `tester1 / tester123` (Tester)
- `dev1 / dev123` (Developer)

## How To Run

1. Open terminal in this folder
2. (Optional) create virtual env: `python -m venv .venv`
3. (Optional) activate (PowerShell): `.venv\Scripts\Activate.ps1`
4. Install requirements: `pip install -r requirements.txt`
5. Start application: `python app.py`
6. Open in browser: `http://localhost:5000/login`

## Project Structure

- `app.py` - run file
- `bug_tracker/__init__.py` - app factory and module registration
- `bug_tracker/db.py` - SQLite setup, schema, seed data
- `bug_tracker/auth.py` - login/logout and session auth
- `bug_tracker/bugs.py` - bug CRUD, status updates, search/filter
- `bug_tracker/templates/` - HTML pages
- `bug_tracker/static/styles.css` - UI styling
- `bugtracker.db` - SQLite database created automatically
