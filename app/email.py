import threading
from flask import current_app
from flask_mail import Message
from app import mail


def _send_async(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.warning(f'Email send failed: {e}')


def _send_email(subject, recipients, body):
    """Send a plain-text email asynchronously. No-ops if mail is not configured."""
    if not current_app.config.get('MAIL_USERNAME'):
        return
    if not recipients:
        return
    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients, body=body)
    thread = threading.Thread(target=_send_async, args=[app, msg], daemon=True)
    thread.start()


def notify_ticket_created(ticket):
    from app.models import User
    admins = User.query.filter_by(role='admin', is_active=True).all()
    recipients = [a.email for a in admins if a.email]
    _send_email(
        subject=f'[HelpDesk] New Ticket #{ticket.id}: {ticket.title}',
        recipients=recipients,
        body=(
            f'A new support ticket has been submitted.\n\n'
            f'Ticket:      #{ticket.id} — {ticket.title}\n'
            f'Category:    {ticket.category}\n'
            f'Priority:    {ticket.priority}\n'
            f'Submitted by: {ticket.submitter.username} ({ticket.submitter.department})\n\n'
            f'Description:\n{ticket.description}'
        ),
    )


def notify_ticket_updated(ticket, old_status):
    if not ticket.submitter.email:
        return
    _send_email(
        subject=f'[HelpDesk] Ticket #{ticket.id} Status Updated',
        recipients=[ticket.submitter.email],
        body=(
            f'Your support ticket has been updated.\n\n'
            f'Ticket:   #{ticket.id} — {ticket.title}\n'
            f'Status:   {old_status} → {ticket.status}\n'
            f'Priority: {ticket.priority}\n'
            f'Assignee: {ticket.assignee.username if ticket.assignee else "Unassigned"}\n'
        ),
    )


def notify_comment_added(ticket, comment):
    recipients = set()
    if ticket.submitter.email and ticket.submitter.id != comment.author_id:
        recipients.add(ticket.submitter.email)
    if ticket.assignee and ticket.assignee.email and ticket.assignee.id != comment.author_id:
        recipients.add(ticket.assignee.email)
    _send_email(
        subject=f'[HelpDesk] New comment on Ticket #{ticket.id}: {ticket.title}',
        recipients=list(recipients),
        body=(
            f'A new comment was added to ticket #{ticket.id}.\n\n'
            f'Ticket: {ticket.title}\n'
            f'Comment by: {comment.author.username}\n\n'
            f'{comment.body}'
        ),
    )
