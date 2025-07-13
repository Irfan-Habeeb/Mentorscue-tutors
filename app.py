import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set appropriate logging level for production
log_level = logging.INFO if os.environ.get('FLASK_ENV') == 'production' else logging.DEBUG
logging.basicConfig(level=log_level)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
# Use proper path for SQLite in production
sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mentorscue.db')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{sqlite_path}")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models here so their tables are created
    import models
    db.create_all()
    
    # Create default admin user if none exists
    from models import Admin
    if not Admin.query.first():
        default_admin = Admin(username='admin')
        default_admin.set_password('admin123')  # Change this in production
        db.session.add(default_admin)
        db.session.commit()
        print("Default admin user created: username='admin', password='admin123'")

# Import routes
import routes

@app.route("/robots.txt")
def robots_txt():
    return app.send_static_file("robots.txt")

# Production-ready: Remove debug mode and app.run() for deployment
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=False)
