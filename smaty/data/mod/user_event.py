import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class UE(SqlAlchemyBase, UserMixin):
    __tablename__ = 'user_events'
    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)
    events = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    public = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return

    '''
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    '''
