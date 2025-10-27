"""
Booking Routes - Flight Search and Booking
"""
from flask import Blueprint, render_template, request
from flask_login import current_user
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
    airports = Airport.query.all()
    flights = []
    search_performed = False
    
    if request.method == 'POST':
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        date_str = request.form.get('date')
        
        search_performed = True
        
        if origin and destination and date_str:
            search_date = datetime.strptime(date_str, '%Y-%m-%d')
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
    
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    num_passengers = int(request.form.get('num_passengers', 1))
    
    booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    total_price = float(flight.price_economy) * num_passengers
    
    booking = Booking(
        booking_reference=booking_ref,
        customer_email=email,
        customer_first_name=first_name,
        customer_last_name=last_name,
        customer_phone=phone,
        flight_id=flight_id,
        user_id=current_user.user_id if current_user.is_authenticated else None,
        num_passengers=num_passengers,
        total_price=total_price,
        booking_date=datetime.now(),
        status='confirmed'
    )
    
    db.session.add(booking)
    flight.available_economy -= num_passengers
    db.session.commit()
    
    return render_template('booking/confirmation.html', booking=booking)

@booking_bp.route('/view', methods=['GET', 'POST'])
def view_booking():
    """View/search for a booking"""
    booking = None
    error = None
    
    if request.method == 'POST':
        booking_ref = request.form.get('booking_reference', '').strip().upper()
        last_name = request.form.get('last_name', '').strip()
        
        if booking_ref and last_name:
            booking = Booking.query.filter_by(
                booking_reference=booking_ref,
                customer_last_name=last_name
            ).first()
            
            if not booking:
                error = "Booking not found. Please check your reference and last name."
        else:
            error = "Please enter both booking reference and last name."
    
    return render_template('booking/view.html', booking=booking, error=error)

@booking_bp.route('/checkin/<booking_ref>')
def checkin(booking_ref):
    """Check-in for a flight"""
    booking = Booking.query.filter_by(booking_reference=booking_ref).first_or_404()
    
    # Check if already checked in
    if booking.checked_in:
        return render_template('booking/boarding_pass.html', booking=booking)
    
    # TESTING MODE: Skip 24-hour check for now
    # from datetime import timedelta
    # now = datetime.now()
    # checkin_opens = booking.flight.scheduled_departure - timedelta(hours=24)
    # if now < checkin_opens:
    #     hours_remaining = int((checkin_opens - now).total_seconds() / 3600)
    #     error = f"Check-in opens {hours_remaining} hours before departure"
    #     return render_template('booking/checkin_error.html', error=error, booking=booking)
    
    # Show seat selection
    return render_template('booking/checkin.html', booking=booking)

@booking_bp.route('/checkin/confirm/<booking_ref>', methods=['POST'])
def confirm_checkin(booking_ref):
    """Confirm check-in and assign seat"""
    booking = Booking.query.filter_by(booking_reference=booking_ref).first_or_404()
    
    seat_number = request.form.get('seat_number')
    
    booking.checked_in = True
    booking.seat_number = seat_number
    
    db.session.commit()
    
    return render_template('booking/boarding_pass.html', booking=booking)
