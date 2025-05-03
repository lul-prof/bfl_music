from flask import Blueprint

# Import all blueprints
from app.routes.main import bp as main_bp
from app.routes.auth import bp as auth_bp
from app.routes.admin import bp as admin_bp
from app.routes.orders import bp as orders_bp
from app.routes.payments import bp as payments_bp

# Create a list of all blueprints to be registered
blueprints = [
    main_bp,
    auth_bp,
    admin_bp,
    orders_bp,
    payments_bp
]

# Function to register all blueprints
def register_blueprints(app):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)