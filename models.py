"""
Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    
    # Required for Flask-Login
    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Relationship to bookings
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Airport(db.Model):
    __tablename__ = 'airports'
    airport_code = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    timezone = db.Column(db.String(50))

class Aircraft(db.Model):
    __tablename__ = 'aircraft'
    aircraft_id = db.Column(db.Integer, primary_key=True)
    registration = db.Column(db.String(10))
    model = db.Column(db.String(50))
    total_seats = db.Column(db.Integer)
    economy_seats = db.Column(db.Integer)
    business_seats = db.Column(db.Integer)
    first_class_seats = db.Column(db.Integer)

class Flight(db.Model):
    __tablename__ = 'flights'
    flight_id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10))
    origin_airport = db.Column(db.String(3), db.ForeignKey('airports.airport_code'))
    destination_airport = db.Column(db.String(3), db.ForeignKey('airports.airport_code'))
    aircraft_id = db.Column(db.Integer, db.ForeignKey('aircraft.aircraft_id'))
    scheduled_departure = db.Column(db.DateTime)
    scheduled_arrival = db.Column(db.DateTime)
    status = db.Column(db.String(20))
    gate = db.Column(db.String(10))
    price_economy = db.Column(db.Numeric(10, 2))
    price_business = db.Column(db.Numeric(10, 2))
    price_first = db.Column(db.Numeric(10, 2))
    available_economy = db.Column(db.Integer)
    available_business = db.Column(db.Integer)
    available_first = db.Column(db.Integer)
    
    # Relationships
    origin = db.relationship('Airport', foreign_keys=[origin_airport])
    destination = db.relationship('Airport', foreign_keys=[destination_airport])
    aircraft = db.relationship('Aircraft')

class Booking(db.Model):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(6), unique=True)
    customer_email = db.Column(db.String(100))
    customer_first_name = db.Column(db.String(50))
    customer_last_name = db.Column(db.String(50))
    customer_phone = db.Column(db.String(20))
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.flight_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    num_passengers = db.Column(db.Integer)
    total_price = db.Column(db.Numeric(10, 2))
    booking_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))
    checked_in = db.Column(db.Boolean, default=False)
    seat_number = db.Column(db.String(5))
    
    # Relationship
    flight = db.relationship('Flight')

class Baggage(db.Model):
    __tablename__ = 'baggage'
    baggage_id = db.Column(db.Integer, primary_key=True)
    baggage_tag = db.Column(db.String(10), unique=True, nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'))
    weight = db.Column(db.Numeric(5, 2))
    status = db.Column(db.String(20), default='checked_in')
    current_location = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200))
    
    # Relationship
    booking = db.relationship('Booking', backref='baggage_items')
