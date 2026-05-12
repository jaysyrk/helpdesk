from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app import db
from app.models import Asset, User
from app.forms import AssetForm

assets_bp = Blueprint('assets', __name__, url_prefix='/assets')


def _admin_required():
    if not current_user.is_admin:
        abort(403)


@assets_bp.route('/')
@login_required
def list_assets():
    assets = Asset.query.order_by(Asset.asset_tag).all()
    return render_template('assets/list.html', assets=assets)


@assets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_asset():
    _admin_required()
    form = AssetForm()
    users = User.query.order_by(User.username).all()
    form.assigned_to_id.choices = [(0, '— Unassigned —')] + [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        asset = Asset(
            asset_tag=form.asset_tag.data,
            name=form.name.data,
            asset_type=form.asset_type.data,
            manufacturer=form.manufacturer.data,
            model=form.model.data,
            serial_number=form.serial_number.data,
            status=form.status.data,
            location=form.location.data,
            assigned_to_id=form.assigned_to_id.data if form.assigned_to_id.data != 0 else None,
            purchase_date=form.purchase_date.data,
            warranty_expiry=form.warranty_expiry.data,
            notes=form.notes.data,
        )
        db.session.add(asset)
        db.session.commit()
        flash(f'Asset {asset.asset_tag} added.', 'success')
        return redirect(url_for('assets.list_assets'))
    return render_template('assets/form.html', form=form, title='New Asset')


@assets_bp.route('/<int:asset_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_asset(asset_id):
    _admin_required()
    asset = Asset.query.get_or_404(asset_id)
    form = AssetForm(obj=asset)
    users = User.query.order_by(User.username).all()
    form.assigned_to_id.choices = [(0, '— Unassigned —')] + [(u.id, u.username) for u in users]

    if form.validate_on_submit():
        asset.asset_tag = form.asset_tag.data
        asset.name = form.name.data
        asset.asset_type = form.asset_type.data
        asset.manufacturer = form.manufacturer.data
        asset.model = form.model.data
        asset.serial_number = form.serial_number.data
        asset.status = form.status.data
        asset.location = form.location.data
        asset.assigned_to_id = form.assigned_to_id.data if form.assigned_to_id.data != 0 else None
        asset.purchase_date = form.purchase_date.data
        asset.warranty_expiry = form.warranty_expiry.data
        asset.notes = form.notes.data
        db.session.commit()
        flash('Asset updated.', 'success')
        return redirect(url_for('assets.list_assets'))
    elif not form.is_submitted():
        form.assigned_to_id.data = asset.assigned_to_id or 0
    return render_template('assets/form.html', form=form, title='Edit Asset', asset=asset)


@assets_bp.route('/<int:asset_id>/delete', methods=['POST'])
@login_required
def delete_asset(asset_id):
    _admin_required()
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    flash('Asset removed.', 'info')
    return redirect(url_for('assets.list_assets'))
