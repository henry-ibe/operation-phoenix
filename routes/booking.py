"""
Booking Routes - Flight Search and Booking
"""
from flask import Blueprint, render_template, request
from datetime import datetime
from sqlalchemy import func
from models import db, Airport, Flight, Booking
import random
import string

# Create blueprint
booking_bp = Blueprint('booking', __name__, url_prefix='/booking')

@booking_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Flight search page"""
    # Get all airports for dropdown
    airports = Airport.query.all()
    
    # Search results
    flights = []
    search_performed = False
    
    if request.method == 'POST':
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        date_str = request.form.get('date')
        
        search_performed = True
        
        if origin and destination and date_str:
            # Parse date
            search_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Search flights
            flights = Flight.query.filter(
                Flight.origin_airport == origin,
                Flight.destination_airport == destination,
                func.date(Flight.scheduled_departure) == search_date.date()
            ).order_by(Flight.scheduled_departure).all()
    
    return render_template('booking/search.html', 
                         airports=airports, 
                         flights=flights,
                         search_performed=search_performed)

@booking_bp.route('/select/<int:flight_id>')
def select_flight(flight_id):
    """Select a flight and enter passenger details"""
    flight = Flight.query.get_or_404(flight_id)
    return render_template('booking/passenger_details.html', flight=flight)

@booking_bp.route('/confirm/<int:flight_id>', methods=['POST'])
def confirm_booking(flight_id):
    """Confirm booking and create record"""
    flight = Flight.query.get_or_404(flight_id)
    
    # Get passenger info from form
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    num_passengers = int(request.form.get('num_passengers', 1))
    
    # Generate booking reference
    booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Calculate total price
    total_price = float(flight.price_economy) * num_passengers
    
    # Create booking
    booking = Booking(
        booking_reference=booking_ref,
        customer_email=email,
        customer_first_name=first_name,
        customer_last_name=last_name,
        customer_phone=phone,
        flight_id=flight_id,
        num_passengers=num_passengers,
        total_price=total_price,
        booking_date=datetime.now(),
        status='confirmed'
    )
    
    db.session.add(booking)
    
    # Update seat availability
    flight.available_economy -= num_passengers
    
    db.session.commit()
    
    return render_template('booking/confirmation.html', booking=booking)
