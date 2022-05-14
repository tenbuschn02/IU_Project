from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import event


# Onle for test purposes
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# All user specific classes (food, tables, guests,..) have a relationship with the user class. It's also used for the login
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
    costs = db.relationship('Costs')
    #food_person = db.relationship('FoodPerson')

# All available groups of guests (currently male, female and child), will be filled automatically after db is being created
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

# Containing all guests, including the user id and a group.
# Column 'invitation_sent' not used yet
class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    invitation_sent = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'))

# Status of inviation (currently Open, Accepted, Delined, and Waiting), will be filled automatically after db is being created
class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))

@event.listens_for(Guest.__table__, 'after_create')
def create_groups(*args, **kwargs):
        db.session.add(Status(name='Open'))  
        db.session.add(Status(name='Accepted'))
        db.session.add(Status(name='Declined'))
        db.session.add(Status(name='Waiting'))
        db.session.commit()

# Ratio with expected share of accepted invitations. Changed on food calculator page
class AcceptedRatio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ratio = db.Column(db.Float)

# Containing all foods added by the user on the food calculator page
class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(150))
    price = db.Column(db.Float)
    amount_1 = db.Column(db.Float)
    amount_2 = db.Column(db.Float)
    amount_3 = db.Column(db.Float)

# Containing tables for guest, maintained on table page
class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(150))
    max_guests = db.Column(db.Integer)
    guest = db.relationship('Guest')

# Containing all additional costs (food exluded)
class Costs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(150))
    price = db.Column(db.Float)
