import os
from flask import Flask
from app.config import config
from app.models import db, User, Role, SystemSetting
from app.auth import auth_bp
from app.user_mgmt import user_mgmt_bp
from app.reports import reports_bp
from app.dashboard import dashboard_bp
from app.swagger import init_swagger

def create_app(test_config=None):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    app.config['SECRET_KEY'] = config.get('app.secret_key', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = config.sqlalchemy_database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    init_swagger(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_mgmt_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(dashboard_bp)

    with app.app_context():
        db.create_all()
        # Create default admin user if absent
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@cth.com',
                full_name='System Administrator',
                is_admin=True
            )
            admin_user.set_password('Admin123!')
            db.session.add(admin_user)

            demo_user = User(
                username='user1',
                email='user1@cth.com',
                full_name='Standard User',
                is_admin=False
            )
            demo_user.set_password('User123!')
            db.session.add(demo_user)

            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
