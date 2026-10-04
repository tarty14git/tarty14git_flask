from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    failed_attempts = db.Column(db.Integer, default=0)
    password_expiry_date = db.Column(db.DateTime, nullable=True)
    otp_code = db.Column(db.String(10), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        # Default password expiry: 90 days
        self.password_expiry_date = datetime.now(timezone.utc) + timedelta(days=90)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_password_expired(self):
        if not self.password_expiry_date:
            return False
        expiry = self.password_expiry_date
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expiry

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name or '',
            'is_admin': self.is_admin,
            'is_locked': self.is_locked,
            'failed_attempts': self.failed_attempts,
            'password_expiry_date': self.password_expiry_date.isoformat() if self.password_expiry_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ReportConfig(db.Model):
    __tablename__ = 'report_configs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    table_name = db.Column(db.String(100), nullable=False)
    selected_fields = db.Column(db.Text, nullable=False) # Comma-separated or JSON string
    where_clause = db.Column(db.String(500), nullable=True)
    order_by = db.Column(db.String(200), nullable=True)
    created_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'table_name': self.table_name,
            'selected_fields': self.selected_fields.split(',') if ',' in self.selected_fields else [self.selected_fields],
            'where_clause': self.where_clause or '',
            'order_by': self.order_by or '',
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'

    setting_key = db.Column(db.String(100), primary_key=True)
    setting_value = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(255), nullable=True)
