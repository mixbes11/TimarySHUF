from sqlalchemy import Column, Integer, ForeignKey, String, Time, Date, orm
from sqlalchemy_serializer import SerializerMixin
from Timary.data.db_session import SqlAlchemyBase


class Timetable(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'timetable'

    lesson_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(Integer, ForeignKey('users.id'))
    lesson = Column(String)
    room = Column(String)
    date = Column(Date)
    time = Column(Time)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = orm.relationship('User', foreign_keys=[id])