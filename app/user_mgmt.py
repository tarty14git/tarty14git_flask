from flask import Blueprint, request, jsonify, session, render_template
from app.models import db, User, AuditLog
from app.config import config

user_mgmt_bp = Blueprint('user_mgmt', __name__)

def require_admin():
    if not session.get('user_id'):
        return False, jsonify({'success': False, 'message': 'Unauthorized'}), 401
    if not session.get('is_admin'):
        return False, jsonify({'success': False, 'message': 'Admin privilege required.'}), 403
    return True, None, None

def log_audit(action, details=None, username=None):
    if not username:
        username = session.get('username', 'anonymous')
    ip = request.remote_addr
    log = AuditLog(username=username, action=action, details=details, ip_address=ip)
    db.session.add(log)
    db.session.commit()

@user_mgmt_bp.route('/users', methods=['GET'])
def list_users():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    users = User.query.all()
    return jsonify({'success': True, 'users': [u.to_dict() for u in users]})

@user_mgmt_bp.route('/users/<int:user_id>/lock', methods=['POST'])
def toggle_lock(user_id):
    is_ok, resp, code = require_admin()
    if not is_ok:
        return resp, code

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    data = request.get_json(silent=True) or {}
    lock_status = data.get('lock', not user.is_locked)

    user.is_locked = lock_status
    if not lock_status:
        user.failed_attempts = 0

    db.session.commit()
    action = 'USER_LOCKED' if user.is_locked else 'USER_UNLOCKED'
    log_audit(action, f"Updated lock status for {user.username} to {user.is_locked}")
    return jsonify({'success': True, 'message': f"User {user.username} lock status updated to {user.is_locked}.", 'user': user.to_dict()})

@user_mgmt_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
def reset_password(user_id):
    is_ok, resp, code = require_admin()
    if not is_ok:
        return resp, code

    data = request.get_json(silent=True) or {}
    new_password = data.get('new_password', 'Password123!')

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    user.set_password(new_password)
    user.is_locked = False
    user.failed_attempts = 0
    db.session.commit()

    log_audit('PASSWORD_RESET', f"Admin reset password for {user.username}")
    return jsonify({'success': True, 'message': f"Password for {user.username} successfully reset."})

@user_mgmt_bp.route('/config/settings', methods=['GET', 'POST'])
def system_settings():
    is_ok, resp, code = require_admin()
    if not is_ok:
        return resp, code

    if request.method == 'GET':
        return jsonify({
            'success': True,
            'app_name': config.get('app.name'),
            'db_type': config.get('db.type'),
            'db_host': config.get('db.host'),
            'db_port': config.get('db.port'),
            'db_name': config.get('db.name'),
            'db_user': config.get('db.user'),
            'auth_ldap_enabled': config.get('auth.ldap.enabled') == 'true',
            '2fa_enabled': config.get('2fa.enabled') == 'true',
            '2fa_method': config.get('2fa.method')
        })

    data = request.get_json(silent=True) or request.form
    if 'app.name' in data:
        config.set('app.name', data['app.name'])
    if 'db.type' in data:
        config.set('db.type', data['db.type'])
    if 'db.host' in data:
        config.set('db.host', data['db.host'])
    if 'db.port' in data:
        config.set('db.port', data['db.port'])
    if 'db.name' in data:
        config.set('db.name', data['db.name'])
    if 'db.user' in data:
        config.set('db.user', data['db.user'])
    if 'db.password' in data and data['db.password']:
        config.set('db.password', data['db.password'])
    if 'auth.ldap.enabled' in data:
        val = 'true' if str(data['auth.ldap.enabled']).lower() in ['true', '1', 'on'] else 'false'
        config.set('auth.ldap.enabled', val)
    if '2fa.enabled' in data:
        val = 'true' if str(data['2fa.enabled']).lower() in ['true', '1', 'on'] else 'false'
        config.set('2fa.enabled', val)
    if '2fa.method' in data:
        config.set('2fa.method', data['2fa.method'])

    config.save()
    log_audit('CONFIG_UPDATED', "System settings updated via Admin UI")
    return jsonify({'success': True, 'message': 'System settings updated successfully.'})
