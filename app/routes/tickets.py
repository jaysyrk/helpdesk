import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, Response
from flask_login import login_required, current_user
from app import db
from app.models import Ticket, User, Comment
from app.forms import TicketForm, TicketUpdateForm, CommentForm
from app import email as mailer

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')


@tickets_bp.route('/')
@login_required
def list_tickets():
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    category_filter = request.args.get('category', '')

    query = Ticket.query
    if not current_user.is_admin:
        query = query.filter_by(submitter_id=current_user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)

    tickets = query.order_by(Ticket.created_at.desc()).all()
    return render_template('tickets/list.html', tickets=tickets,
                           status_filter=status_filter,
                           priority_filter=priority_filter,
                           category_filter=category_filter)


@tickets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            priority=form.priority.data,
            submitter_id=current_user.id
        )
        db.session.add(ticket)
        db.session.commit()
        flash(f'Ticket #{ticket.id} submitted successfully.', 'success')
        mailer.notify_ticket_created(ticket)
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))
    return render_template('tickets/new.html', form=form)


@tickets_bp.route('/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not current_user.is_admin and ticket.submitter_id != current_user.id:
        abort(403)

    comment_form = CommentForm()
    update_form = None
    if current_user.is_admin:
        update_form = TicketUpdateForm()
        agents = User.query.filter_by(role='admin').all()
        update_form.assignee_id.choices = [(0, '— Unassigned —')] + [(u.id, u.username) for u in agents]
        if not update_form.is_submitted():
            update_form.status.data = ticket.status
            update_form.priority.data = ticket.priority
            update_form.assignee_id.data = ticket.assignee_id or 0

    if comment_form.validate_on_submit() and 'body' in request.form:
        comment = Comment(body=comment_form.body.data, ticket_id=ticket.id, author_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        mailer.notify_comment_added(ticket, comment)
        flash('Comment added.', 'success')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))

    comments = ticket.comments.order_by(Comment.created_at.asc()).all()
    return render_template('tickets/view.html', ticket=ticket,
                           comment_form=comment_form, update_form=update_form,
                           comments=comments)


@tickets_bp.route('/<int:ticket_id>/update', methods=['POST'])
@login_required
def update_ticket(ticket_id):
    if not current_user.is_admin:
        abort(403)
    ticket = Ticket.query.get_or_404(ticket_id)
    agents = User.query.filter_by(role='admin').all()
    form = TicketUpdateForm()
    form.assignee_id.choices = [(0, '— Unassigned —')] + [(u.id, u.username) for u in agents]

    if form.validate_on_submit():
        old_status = ticket.status
        ticket.status = form.status.data
        ticket.priority = form.priority.data
        ticket.assignee_id = form.assignee_id.data if form.assignee_id.data != 0 else None
        ticket.updated_at = datetime.utcnow()
        if form.status.data in ('Resolved', 'Closed') and not ticket.resolved_at:
            ticket.resolved_at = datetime.utcnow()
        db.session.commit()
        if old_status != ticket.status:
            mailer.notify_ticket_updated(ticket, old_status)
        flash('Ticket updated.', 'success')
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))


@tickets_bp.route('/<int:ticket_id>/delete', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    if not current_user.is_admin:
        abort(403)
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket deleted.', 'info')
    return redirect(url_for('tickets.list_tickets'))


@tickets_bp.route('/export')
@login_required
def export_csv():
    if current_user.is_admin:
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    else:
        tickets = Ticket.query.filter_by(submitter_id=current_user.id).order_by(Ticket.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'ID', 'Title', 'Category', 'Priority', 'Status',
        'Submitter', 'Assignee', 'SLA Deadline', 'Overdue',
        'Hours Open', 'Created', 'Resolved',
    ])
    for t in tickets:
        writer.writerow([
            t.id,
            t.title,
            t.category,
            t.priority,
            t.status,
            t.submitter.username,
            t.assignee.username if t.assignee else '',
            t.sla_deadline.strftime('%Y-%m-%d %H:%M'),
            'Yes' if t.is_overdue else 'No',
            f'{t.hours_open:.1f}',
            t.created_at.strftime('%Y-%m-%d %H:%M'),
            t.resolved_at.strftime('%Y-%m-%d %H:%M') if t.resolved_at else '',
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=tickets_export.csv'},
    )
