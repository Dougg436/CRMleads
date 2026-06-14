from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
import os

# Inicialização das extensões
db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()


def create_app(config_name=None):
    """Factory function para criar e configurar a aplicação Flask"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Carrega configurações
    app.config.from_object(config[config_name])
    
    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Configurações do login_manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Registra blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.leads.routes import leads_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(leads_bp)
    
    # Contexto da aplicação para criação de tabelas
    with app.app_context():
        from app.models.user import User
        from app.models.lead import Lead
        
        db.create_all()
    
    return app
