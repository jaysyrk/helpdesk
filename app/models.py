from datetime import datetime, timedelta
from flask_login import UserMixin
from app import db, login_manager

# SLA thresholds in hours per priority level
SLA_HOURS = {'Critical': 4, 'High': 24, 'Medium': 48, 'Low': 72}


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    department = db.Column(db.String(64), nullable=False, default='General')
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default='1')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tickets_submitted = db.relationship('Ticket', foreign_keys='Ticket.submitter_id', backref='submitter', lazy='dynamic')
    tickets_assigned = db.relationship('Ticket', foreign_keys='Ticket.assignee_id', backref='assignee', lazy='dynamic')

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General')
    priority = db.Column(db.String(20), nullable=False, default='Medium')  # Low / Medium / High / Critical
    status = db.Column(db.String(20), nullable=False, default='Open')      # Open / In Progress / Resolved / Closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    comments = db.relationship('Comment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def sla_deadline(self):
        hours = SLA_HOURS.get(self.priority, 48)
        return self.created_at + timedelta(hours=hours)

    @property
    def is_overdue(self):
        if self.status in ('Resolved', 'Closed'):
            return False
        return datetime.utcnow() > self.sla_deadline

    @property
    def hours_open(self):
        end = self.resolved_at or datetime.utcnow()
        return (end - self.created_at).total_seconds() / 3600

    def __repr__(self):
        return f'<Ticket #{self.id} {self.title}>'


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref='comments')

    def __repr__(self):
        return f'<Comment {self.id}>'


class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)   # Laptop / Desktop / Server / Network / Peripheral / Other
    manufacturer = db.Column(db.String(64), nullable=True)
    model = db.Column(db.String(64), nullable=True)
    serial_number = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(30), nullable=False, default='Active')  # Active / Inactive / In Repair / Retired
    location = db.Column(db.String(64), nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_to = db.relationship('User', backref='assets')
    purchase_date = db.Column(db.Date, nullable=True)
    warranty_expiry = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Asset {self.asset_tag} {self.name}>'
