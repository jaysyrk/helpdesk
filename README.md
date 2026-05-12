# HelpDesk Pro — IT Help Desk & Asset Management System

A full-stack web application built with Python/Flask demonstrating core concepts from both **Management Information Systems (MIS)** and **Computer Information Technology (CIT)**.

## Features

### Help Desk Ticketing (CIT)
- Submit, track, and resolve IT support tickets
- Categories: Hardware, Software, Network, Account/Access, Security
- Priority levels: Low / Medium / High / Critical
- Status workflow: Open → In Progress → Resolved → Closed
- Threaded comments on each ticket
- Admin ticket assignment and management

### Asset Inventory Management (MIS)
- Track all IT assets with asset tags, serial numbers, and warranty dates
- Asset types: Laptop, Desktop, Server, Network Device, Peripheral
- Assign assets to users, track location and status
- Status tracking: Active / Inactive / In Repair / Retired

### Business Intelligence Dashboard (MIS)
- Live KPI cards (open tickets, active assets, resolution rate)
- Chart.js visualizations: tickets by status, priority, category
- Recent activity feed

### Authentication & Access Control
- Secure login with hashed passwords (Werkzeug PBKDF2)
- Role-based access: Admin vs. regular user
- CSRF protection on all forms
- Users only see their own tickets; admins see all

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask 3 |
| Database | SQLite + SQLAlchemy ORM |
| Auth | Flask-Login + Werkzeug |
| Forms | Flask-WTF + WTForms |
| Frontend | Bootstrap 5, Chart.js, Bootstrap Icons |

## Project Structure

```
rit-helpdesk/
├── run.py               # Entry point
├── config.py            # Configuration
├── requirements.txt
└── app/
    ├── __init__.py      # App factory
    ├── models.py        # SQLAlchemy models (User, Ticket, Comment, Asset)
    ├── forms.py         # WTForms form classes
    ├── routes/
    │   ├── auth.py      # Login / register / logout
    │   ├── tickets.py   # Ticket CRUD
    │   ├── assets.py    # Asset CRUD
    │   └── dashboard.py # Dashboard & API stats
    ├── templates/
    │   ├── base.html
    │   ├── dashboard.html
    │   ├── auth/
    │   ├── tickets/
    │   ├── assets/
    │   └── partials/
    └── static/
        └── css/style.css
```

## Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python run.py

# 3. Open in browser
# http://127.0.0.1:5000
```

**Default admin account:** `admin` / `admin123`

## Database Models

- **User** — username, email, department, role (admin/user)
- **Ticket** — title, description, category, priority, status, timestamps, submitter/assignee FKs
- **Comment** — body, timestamp, ticket/author FKs
- **Asset** — asset tag, type, manufacturer, model, serial, location, status, assigned user, purchase/warranty dates

---

Built as a portfolio project for RIT MIS/CIT application.
