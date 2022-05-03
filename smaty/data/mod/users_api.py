import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/news')
def get_news():
    return "Обработчик в news_api"