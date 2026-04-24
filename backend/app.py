from flask import Flask
from config import Config, TEMPLATE_FOLDER, STATIC_FOLDER

def create_app():
    # Initialize the Flask App
    app = Flask(__name__, 
                template_folder=TEMPLATE_FOLDER, 
                static_folder=STATIC_FOLDER)
                
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize Extensions
    from extensions import mail
    mail.init_app(app)
    
    # Import Blueprints
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    from routes.appointment_routes import appointment_bp
    from routes.admin_routes import admin_bp
    from routes.main_routes import main_bp
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
