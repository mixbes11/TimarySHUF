from sqlalchemy import Column, Integer, ForeignKey, String, Time, Date, orm
from sqlalchemy_serializer import SerializerMixin

from Timary.data.db_session import SqlAlchemyBase


class Homework(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'homework'

    id = Column(Integer, ForeignKey('users.id'))
    homework_id = Column(Integer, primary_key=True, autoincrement=True)
    task = Column(String)
    lesson = Column(String)
    date = Column(Date)
    ready = Column(String)
    file = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = orm.relationship('User', foreign_keys=[id])