from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
from enum import Enum

USER_ID_FIELD = 'user.id'


class UserRole(Enum):
    USER = 'user'
    VOLUNTEER = 'volunteer'
    ADMIN = 'admin'

    @classmethod
    def choices(cls):
        return [(role.value, role.name) for role in cls]


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default=UserRole.USER.value, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_response_read_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_notification_dismissed = db.Column(db.DateTime, default=datetime.utcnow)

    animals = db.relationship('Animal', backref='owner', lazy='dynamic')
    adoptions = db.relationship('Adoption', backref='user', lazy='dynamic')
    lost_found_reports = db.relationship('LostFoundReport', backref='author', lazy='dynamic')
    chatbot_feedback = db.relationship('ChatbotFeedback', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN.value

    @property
    def is_volunteer(self):
        return self.role == UserRole.VOLUNTEER.value

    def has_role(self, role):
        if isinstance(role, UserRole):
            role = role.value
        return self.role == role

    def has_permission(self, permission):
        if self.is_admin:
            return True

        permissions = {
            'view_animals': [UserRole.USER.value, UserRole.VOLUNTEER.value],
            'apply_adoption': [UserRole.USER.value, UserRole.VOLUNTEER.value],
            'create_lost_found': [UserRole.USER.value, UserRole.VOLUNTEER.value],
            'view_events': [UserRole.USER.value, UserRole.VOLUNTEER.value],
            'join_event': [UserRole.USER.value, UserRole.VOLUNTEER.value],

            'create_animal': [UserRole.VOLUNTEER.value],
            'edit_animal': [UserRole.VOLUNTEER.value],
            'review_adoption': [UserRole.VOLUNTEER.value],
            'manage_events': [UserRole.VOLUNTEER.value],
            'create_event': [UserRole.VOLUNTEER.value],
            'moderate_forum': [UserRole.VOLUNTEER.value],

            'manage_users': [UserRole.ADMIN.value],
            'delete_animal': [UserRole.ADMIN.value],
            'delete_user': [UserRole.ADMIN.value],
            'assign_roles': [UserRole.ADMIN.value],
            'view_statistics': [UserRole.ADMIN.value],
        }

        return self.role in permissions.get(permission, [])

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

    def new_responses_count(self):
        """Return the count of unread responses to user's reports."""
        return ReportResponse.query.join(LostFoundReport).filter(
            LostFoundReport.user_id == self.id,
            ReportResponse.timestamp > (self.last_response_read_time or datetime.min),
            ReportResponse.responder_id != self.id
        ).count()

    def has_new_responses(self):
        """Check if user has new responses and hasn't dismissed the notification."""
        return (self.new_responses_count() > 0 and
                (not self.last_notification_dismissed or
                 self.last_notification_dismissed < self.last_response_read_time))


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Animal(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(100))
    age = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    size = db.Column(db.String(10))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='available')
    image_url = db.Column(db.String(200))
    good_with_children = db.Column(db.Boolean, default=False)
    good_with_other_animals = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID_FIELD))

    adoptions = db.relationship('Adoption', backref='animal', lazy='dynamic')

    def __repr__(self):
        return f'<Animal {self.name}>'


class Adoption(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id', name='fk_adoption_animal'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID_FIELD, name='fk_adoption_user'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('adoption_application.id', name='fk_adoption_application'),
                               nullable=False)
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)

    application = db.relationship('AdoptionApplication', backref='adoption', uselist=False)

    def __repr__(self):
        return f'<Adoption {self.id}>'


class AdoptionApplication(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID_FIELD), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    housing_type = db.Column(db.String(50), nullable=False)
    landlord_permission = db.Column(db.Boolean, default=False)
    yard = db.Column(db.Boolean, default=False)
    previous_pets = db.Column(db.Text)
    current_pets = db.Column(db.Text)
    vet_reference = db.Column(db.Text)
    adoption_reason = db.Column(db.Text, nullable=False)
    care_plan = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    updated_by = db.Column(db.Integer, db.ForeignKey(USER_ID_FIELD))

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('adoption_applications', lazy='dynamic'))
    animal = db.relationship('Animal', backref=db.backref('adoption_applications', lazy='dynamic'))
    updated_by_user = db.relationship('User', foreign_keys=[updated_by])

    def __repr__(self):
        return f'<AdoptionApplication {self.id}>'


class LostFoundReport(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(10), nullable=False)
    animal_type = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100))
    breed = db.Column(db.String(100))
    color = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    last_seen_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))

    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)

    has_collar = db.Column(db.Boolean, default=False)
    is_microchipped = db.Column(db.Boolean, default=False)
    special_needs = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID_FIELD))

    def __repr__(self):
        return f'<LostFoundReport {self.id}>'


class ChatbotFeedback(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(USER_ID_FIELD))
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    using_fallback = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ChatbotFeedback {self.id}>'


class ReportResponse(db.Model):
    __table_args__ = (
        db.Index('ix_report_response_timestamp', 'timestamp'),
    )

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('lost_found_report.id', ondelete='CASCADE', name='fk_report_response_report'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey(USER_ID_FIELD, ondelete='CASCADE', name='fk_report_response_responder'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    report = db.relationship('LostFoundReport', backref=db.backref('responses', cascade='all, delete-orphan'))
    responder = db.relationship('User', backref=db.backref('sent_responses', cascade='all, delete-orphan'))

