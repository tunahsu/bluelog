from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_login import LoginManager

bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
ckeditor = CKEditor()
moment = Moment()
login_manager = LoginManager()
