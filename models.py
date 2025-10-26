"""
Database Models
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    num_passengers = db.Column(db.Integer)
    total_price = db.Column(db.Numeric(10, 2))
    booking_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))
    
    # Relationship
    flight = db.relationship('Flight')
