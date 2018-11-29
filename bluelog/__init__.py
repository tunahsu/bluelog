import os
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFError

from bluelog.setting import config
from bluelog.extensions import bootstrap, db, mail, ckeditor, moment

from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.blog import blog_bp

# when use [flask run], it will automatically invoke the function named create_app() / make_app()
def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')
    app.config.from_object(config[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errors(app)
    register_shell_context(app)
    register_template_context(app)
    return app


def register_logging(app):
    pass


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    moment.init_app(app)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_commands(app):
    pass


def register_errors(app):
    # bad request / invalid hostname
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    # page not found
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    # server error
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # csrf error
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400

# when use [flask shell], it will invoke the function and register the items
def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_template_context(app):
    pass
