import random
import string
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from app.models import db, User, AuditLog
from app.config import config
from app.ldap_auth import authenticate_ldap

auth_bp = Blueprint('auth', __name__)

def log_audit(action, details=None, username=None):
    if not username:
        username = session.get('username', 'anonymous')
    ip = request.remote_addr
    log = AuditLog(username=username, action=action, details=details, ip_address=ip)
    db.session.add(log)
    db.session.commit()

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', app_name=config.get('app.name', 'CTH Enterprise Portal'))

    data = request.get_json(silent=True) or request.form
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required.'}), 400

    user = User.query.filter_by(username=username).first()

    # Check LDAP authentication mode
    ldap_enabled = config.get('auth.ldap.enabled', 'false').lower() == 'true'

    if ldap_enabled:
        success, msg = authenticate_ldap(username, password)
        if not success:
            log_audit('LOGIN_FAILED_LDAP', f"Failed LDAP login for {username}", username=username)
            return jsonify({'success': False, 'message': msg}), 401

        # Provision or retrieve local user record for session/permissions
        if not user:
            user = User(
                username=username,
                email=f"{username}@domain.com",
                full_name=username.capitalize(),
                is_admin=True if username == 'ldapadmin' else False
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
    else:
        # Local Database Authentication
        if not user:
            log_audit('LOGIN_FAILED', f"User not found: {username}", username=username)
            return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

        if user.is_locked:
            log_audit('LOGIN_LOCKED', f"Locked user attempted login: {username}", username=username)
            return jsonify({'success': False, 'message': 'Account is locked. Please contact administrator.'}), 403

        if not user.check_password(password):
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.is_locked = True
                log_audit('ACCOUNT_LOCKED', f"Account locked due to 5 failed attempts: {username}", username=username)
            db.session.commit()
            return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

        if user.is_password_expired():
            log_audit('LOGIN_EXPIRED_PWD', f"Password expired for user {username}", username=username)
            return jsonify({'success': False, 'message': 'Password has expired. Please reset password.', 'require_reset': True}), 403

        user.failed_attempts = 0
        db.session.commit()

    # Check 2FA requirement
    two_fa_enabled = config.get('2fa.enabled', 'false').lower() == 'true'
    if two_fa_enabled:
        otp = generate_otp()
        user.otp_code = otp
        user.otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
        db.session.commit()

        session['pending_2fa_user'] = user.username
        # Demo simulation: Print/Return OTP in response for testing
        log_audit('2FA_SENT', f"2FA OTP generated for {user.username}: {otp}", username=user.username)
        return jsonify({
            'success': True,
            'require_2fa': True,
            'message': f"2FA OTP code sent via {config.get('2fa.method', 'email')} (Demo OTP: {otp})"
        })

    session['user_id'] = user.id
    session['username'] = user.username
    session['is_admin'] = user.is_admin
    log_audit('LOGIN_SUCCESS', f"User logged in successfully: {username}", username=username)

    if request.is_json:
        return jsonify({'success': True, 'redirect': url_for('dashboard.index')})
    return redirect(url_for('dashboard.index'))

@auth_bp.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json(silent=True) or request.form
    username = session.get('pending_2fa_user')
    otp = data.get('otp', '').strip()

    if not username or not otp:
        return jsonify({'success': False, 'message': 'Missing session user or OTP code.'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.otp_code:
        return jsonify({'success': False, 'message': 'Invalid session or 2FA request.'}), 400

    now = datetime.now(timezone.utc)
    expiry = user.otp_expiry
    if expiry and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if now > expiry or user.otp_code != otp:
        log_audit('2FA_FAILED', f"Invalid or expired OTP for {username}", username=username)
        return jsonify({'success': False, 'message': 'Invalid or expired OTP code.'}), 400

    # Clear OTP
    user.otp_code = None
    user.otp_expiry = None
    db.session.commit()

    session.pop('pending_2fa_user', None)
    session['user_id'] = user.id
    session['username'] = user.username
    session['is_admin'] = user.is_admin
    log_audit('2FA_SUCCESS', f"2FA verified successfully for {username}", username=username)

    return jsonify({'success': True, 'redirect': url_for('dashboard.index')})

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    username = session.get('username')
    if username:
        log_audit('LOGOUT', f"User logged out: {username}", username=username)
    session.clear()
    if request.is_json:
        return jsonify({'success': True, 'redirect': url_for('auth.login')})
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or request.form
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()

    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'Username, email, and password are required.'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'success': False, 'message': 'Username or Email already exists.'}), 400

    new_user = User(username=username, email=email, full_name=full_name)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    log_audit('USER_REGISTERED', f"New user account created: {username}", username=username)

    two_fa_enabled = config.get('2fa.enabled', 'false').lower() == 'true'
    msg = "Account created successfully."
    if two_fa_enabled:
        msg += " Welcome notification sent via simulated " + config.get('2fa.method', 'email') + "."

    return jsonify({'success': True, 'message': msg})
