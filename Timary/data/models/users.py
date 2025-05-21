from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from ..db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String)
    name = Column(String)
    email = Column(String, index=True, unique=True)
    hashed_password = Column(String)
    theme = Column(String)

    timetable = orm.relationship('Timetable', back_populates='user', foreign_keys='Timetable.id')
    homework = orm.relationship('Homework', back_populates='user', foreign_keys='Homework.id')


    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)