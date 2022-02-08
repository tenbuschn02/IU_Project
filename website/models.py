from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import event



class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    guests = db.relationship('Guest')
    accepted_ratio = db.relationship('AcceptedRatio')
    food = db.relationship('Food')
    table = db.relationship('Table')
    #food_person = db.relationship('FoodPerson')

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    #food = db.relationship('FoodPerson')

@event.listens_for(Group.__table__, 'after_create')
def create_groups(*args, **kwargs):
        db.session.add(Group(name='Male'))
        db.session.add(Group(name='Female'))
        db.session.add(Group(name='Child'))
        db.session.commit()


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    invitation_sent = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))

@event.listens_for(Guest.__table__, 'after_create')
def create_groups(*args, **kwargs):
        db.session.add(Group(name='Open'))
        db.session.add(Group(name='Accepted'))
        db.session.add(Group(name='Declined'))
        db.session.add(Group(name='Waiting'))
        db.session.commit()


class AcceptedRatio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ratio = db.Column(db.Float)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(150))
    price = db.Column(db.Float)
    amount_1 = db.Column(db.Float)
    amount_2 = db.Column(db.Float)
    amount_3 = db.Column(db.Float)

class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(150))
    max_guests = db.Column(db.Integer)

# class FoodPerson(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     food_id = db.Column(db.Integer, db.ForeignKey('food.id'))
#     group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
#     amount = db.Column(db.Float)
