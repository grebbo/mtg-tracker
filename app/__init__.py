import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    test_mode = os.environ.get('MTG_TEST_MODE', '').lower() in ('1', 'true', 'yes')

    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(base_dir, '..', 'data', 'test' if test_mode else '')
    data_dir = os.path.normpath(data_dir)
    os.makedirs(data_dir, exist_ok=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(data_dir, "mtg.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DATA_DIR'] = data_dir
    app.config['TEST_MODE'] = test_mode

    db.init_app(app)

    with app.app_context():
        from app import models
        if test_mode:
            db.drop_all()
        db.create_all()
        models.seed_initial_data()

    from app.routes import main
    app.register_blueprint(main)

    return app
