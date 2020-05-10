import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Vote(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Vote'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    flag = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("User.id"))
    poll_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("Poll.id"))