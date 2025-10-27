"""
Booking Routes - Flight Search and Booking
"""
from flask import Blueprint, render_template, request
from flask_login import current_user
from datetime import datetime
from sqlalchemy import func
from models import db, Airport, Flight, Booking, Baggage
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
    
    # Show seat selection and baggage
    return render_template('booking/checkin.html', booking=booking)

@booking_bp.route('/checkin/confirm/<booking_ref>', methods=['POST'])
def confirm_checkin(booking_ref):
    """Confirm check-in and assign seat"""
    booking = Booking.query.filter_by(booking_reference=booking_ref).first_or_404()
    
    seat_number = request.form.get('seat_number')
    
    # Update booking
    booking.checked_in = True
    booking.seat_number = seat_number
    
    # Process baggage
    baggage_weights = request.form.getlist('baggage_weight[]')
    baggage_descriptions = request.form.getlist('baggage_description[]')
    
    for i, weight in enumerate(baggage_weights):
        if weight:  # Only add if weight is provided
            # Generate baggage tag
            baggage_tag = f"BA{random.randint(100000, 999999)}"
            
            description = baggage_descriptions[i] if i < len(baggage_descriptions) else "Checked bag"
            
            baggage = Baggage(
                baggage_tag=baggage_tag,
                booking_id=booking.booking_id,
                weight=float(weight),
                status='checked_in',
                current_location=f"{booking.flight.origin_airport} - Check-in Counter",
                last_updated=datetime.now(),
                description=description
            )
            
            db.session.add(baggage)
    
    db.session.commit()
    
    return render_template('booking/boarding_pass.html', booking=booking)

@booking_bp.route('/baggage/track', methods=['GET', 'POST'])
def track_baggage():
    """Track baggage by tag number"""
    baggage = None
    error = None
    
    if request.method == 'POST':
        tag = request.form.get('baggage_tag', '').strip().upper()
        
        if tag:
            baggage = Baggage.query.filter_by(baggage_tag=tag).first()
            
            if not baggage:
                error = "Baggage not found. Please check your tag number."
        else:
            error = "Please enter a baggage tag number."
    
    return render_template('booking/track_baggage.html', baggage=baggage, error=error)

@booking_bp.route('/baggage/admin/<baggage_tag>', methods=['GET', 'POST'])
def admin_baggage(baggage_tag):
    """Admin page to update baggage status (DEMO)"""
    from flask import flash, redirect
    
    baggage = Baggage.query.filter_by(baggage_tag=baggage_tag).first_or_404()
    
    if request.method == 'POST':
        new_status = request.form.get('status')
        new_location = request.form.get('location')
        
        baggage.status = new_status
        baggage.current_location = new_location
        baggage.last_updated = datetime.now()
        
        db.session.commit()
        
        flash(f'Baggage {baggage_tag} status updated to {new_status}!', 'success')
        return redirect(f'/booking/baggage/track')
    
    return render_template('booking/admin_baggage.html', baggage=baggage)

@booking_bp.route('/health-check')
def health_check():
    """Detailed system health check"""
    from flask import jsonify
    
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check database
    try:
        db.session.execute(db.text('SELECT 1'))
        db.session.execute(db.text('SELECT COUNT(*) FROM flights'))
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check tables exist
    try:
        Airport.query.first()
        Flight.query.first()
        Booking.query.first()
        health_status['checks']['tables'] = 'healthy'
    except Exception as e:
        health_status['checks']['tables'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    return jsonify(health_status)
