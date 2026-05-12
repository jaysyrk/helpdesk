from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    department = StringField('Department', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class TicketForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(5, 120)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(10)])
    category = SelectField('Category', choices=[
        ('Hardware', 'Hardware'),
        ('Software', 'Software'),
        ('Network', 'Network'),
        ('Account / Access', 'Account / Access'),
        ('Security', 'Security'),
        ('Other', 'Other'),
    ])
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ])
    submit = SubmitField('Submit Ticket')


class TicketUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ])
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ])
    assignee_id = SelectField('Assign To', coerce=int, validators=[Optional()])
    submit = SubmitField('Update Ticket')


class CommentForm(FlaskForm):
    body = TextAreaField('Add Comment', validators=[DataRequired(), Length(1, 1000)])
    submit = SubmitField('Post Comment')


class AssetForm(FlaskForm):
    asset_tag = StringField('Asset Tag', validators=[DataRequired(), Length(1, 30)])
    name = StringField('Asset Name', validators=[DataRequired(), Length(1, 120)])
    asset_type = SelectField('Type', choices=[
        ('Laptop', 'Laptop'),
        ('Desktop', 'Desktop'),
        ('Server', 'Server'),
        ('Network', 'Network Device'),
        ('Peripheral', 'Peripheral'),
        ('Other', 'Other'),
    ])
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=64)])
    model = StringField('Model', validators=[Optional(), Length(max=64)])
    serial_number = StringField('Serial Number', validators=[Optional(), Length(max=64)])
    status = SelectField('Status', choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('In Repair', 'In Repair'),
        ('Retired', 'Retired'),
    ])
    location = StringField('Location', validators=[Optional(), Length(max=64)])
    assigned_to_id = SelectField('Assigned To', coerce=int, validators=[Optional()])
    purchase_date = DateField('Purchase Date', validators=[Optional()])
    warranty_expiry = DateField('Warranty Expiry', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Asset')
