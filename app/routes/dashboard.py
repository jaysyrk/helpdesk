from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import Ticket, Asset, User, Comment
from app import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Ticket stats
    total_tickets = Ticket.query.count()
    open_tickets = Ticket.query.filter_by(status='Open').count()
    in_progress = Ticket.query.filter_by(status='In Progress').count()
    resolved = Ticket.query.filter(Ticket.status.in_(['Resolved', 'Closed'])).count()

    # Overdue SLA count
    active_tickets = Ticket.query.filter(Ticket.status.in_(['Open', 'In Progress'])).all()
    overdue_count = sum(1 for t in active_tickets if t.is_overdue)
    overdue_tickets = [t for t in active_tickets if t.is_overdue][:5]

    # Asset stats
    total_assets = Asset.query.count()
    active_assets = Asset.query.filter_by(status='Active').count()
    in_repair = Asset.query.filter_by(status='In Repair').count()

    # Recent tickets
    recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()

    # Priority distribution (for chart)
    priority_data = db.session.query(
        Ticket.priority, func.count(Ticket.id)
    ).group_by(Ticket.priority).all()

    # Category distribution (for chart)
    category_data = db.session.query(
        Ticket.category, func.count(Ticket.id)
    ).group_by(Ticket.category).all()

    # Status distribution (for chart)
    status_data = db.session.query(
        Ticket.status, func.count(Ticket.id)
    ).group_by(Ticket.status).all()

    # Asset type distribution
    asset_type_data = db.session.query(
        Asset.asset_type, func.count(Asset.id)
    ).group_by(Asset.asset_type).all()

    return render_template('dashboard.html',
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        in_progress=in_progress,
        resolved=resolved,
        overdue_count=overdue_count,
        overdue_tickets=overdue_tickets,
        total_assets=total_assets,
        active_assets=active_assets,
        in_repair=in_repair,
        recent_tickets=recent_tickets,
        priority_data=priority_data,
        category_data=category_data,
        status_data=status_data,
        asset_type_data=asset_type_data,
    )


@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """JSON endpoint for live chart refresh."""
    priority_data = db.session.query(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority).all()
    status_data = db.session.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
    return jsonify({
        'priority': {r[0]: r[1] for r in priority_data},
        'status': {r[0]: r[1] for r in status_data},
    })
