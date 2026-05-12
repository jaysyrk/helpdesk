from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _admin_required():
    if not current_user.is_admin:
        abort(403)


@admin_bp.route('/users')
@login_required
def users():
    _admin_required()
    all_users = User.query.order_by(User.username).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/<int:user_id>/toggle-role', methods=['POST'])
@login_required
def toggle_role(user_id):
    _admin_required()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't change your own role.", 'warning')
        return redirect(url_for('admin.users'))
    user.role = 'user' if user.role == 'admin' else 'admin'
    db.session.commit()
    flash(f"'{user.username}' is now a {user.role}.", 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
def toggle_active(user_id):
    _admin_required()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't deactivate your own account.", 'warning')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f"'{user.username}' has been {status}.", 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    _admin_required()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't delete your own account.", 'warning')
        return redirect(url_for('admin.users'))
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{username}' has been deleted.", 'info')
    return redirect(url_for('admin.users'))
