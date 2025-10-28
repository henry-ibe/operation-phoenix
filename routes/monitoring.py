"""
Monitoring Routes - Health Checks for All Services
"""
from flask import Blueprint, jsonify, render_template
from models import db, Flight, Booking, User, Baggage, Airport
from datetime import datetime
import time

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')

def check_service_health(service_name, check_function):
    """Generic health check wrapper"""
    start_time = time.time()
    try:
        check_function()
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        return {
            'service': service_name,
            'status': 'UP',
            'response_time_ms': round(response_time, 2),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            'service': service_name,
            'status': 'DOWN',
            'error': str(e),
            'response_time_ms': round(response_time, 2),
            'timestamp': datetime.now().isoformat()
        }

@monitoring_bp.route('/health/database')
def health_database():
    """Check database connectivity"""
    def check():
        db.session.execute(db.text('SELECT 1'))
        db.session.execute(db.text('SELECT COUNT(*) FROM flights'))
    return jsonify(check_service_health('database', check))

@monitoring_bp.route('/health/flight-search')
def health_flight_search():
    """Check flight search functionality"""
    def check():
        flights = Flight.query.limit(1).all()
        if not flights:
            raise Exception("No flights available")
    return jsonify(check_service_health('flight_search', check))

@monitoring_bp.route('/health/booking')
def health_booking():
    """Check booking system"""
    def check():
        # Check if bookings table is accessible
        Booking.query.limit(1).all()
        # Check if we can query flights for booking
        Flight.query.filter_by(status='scheduled').limit(1).all()
    return jsonify(check_service_health('booking', check))

@monitoring_bp.route('/health/checkin')
def health_checkin():
    """Check check-in system"""
    def check():
        # Verify we can access bookings for check-in
        Booking.query.filter_by(checked_in=False).limit(1).all()
        # Verify flights table is accessible
        Flight.query.limit(1).all()
    return jsonify(check_service_health('checkin', check))

@monitoring_bp.route('/health/baggage')
def health_baggage():
    """Check baggage tracking system"""
    def check():
        # Verify baggage table is accessible
        Baggage.query.limit(1).all()
        # Check if we can track a baggage item
        db.session.execute(db.text('SELECT COUNT(*) FROM baggage'))
    return jsonify(check_service_health('baggage_tracking', check))

@monitoring_bp.route('/health/authentication')
def health_authentication():
    """Check authentication system"""
    def check():
        # Verify users table is accessible
        User.query.limit(1).all()
        # Check user count
        db.session.execute(db.text('SELECT COUNT(*) FROM users'))
    return jsonify(check_service_health('authentication', check))

@monitoring_bp.route('/health/all')
def health_all():
    """Comprehensive health check of all services"""
    services = {
        'database': health_database(),
        'flight_search': health_flight_search(),
        'booking': health_booking(),
        'checkin': health_checkin(),
        'baggage_tracking': health_baggage(),
        'authentication': health_authentication()
    }
    
    # Get JSON data from each response
    services_status = {k: v.get_json() for k, v in services.items()}
    
    # Calculate overall health
    all_up = all(s['status'] == 'UP' for s in services_status.values())
    
    return jsonify({
        'overall_status': 'UP' if all_up else 'DEGRADED',
        'services': services_status,
        'timestamp': datetime.now().isoformat()
    })

@monitoring_bp.route('/metrics/business')
def metrics_business():
    """Business metrics for monitoring"""
    from sqlalchemy import func
    
    try:
        total_bookings = Booking.query.count()
        total_checkins = Booking.query.filter_by(checked_in=True).count()
        total_users = User.query.count()
        total_baggage = Baggage.query.count()
        total_flights = Flight.query.count()
        revenue = db.session.query(func.sum(Booking.total_price)).scalar() or 0
        
        return jsonify({
            'total_bookings': total_bookings,
            'total_checkins': total_checkins,
            'pending_checkins': total_bookings - total_checkins,
            'total_users': total_users,
            'total_baggage': total_baggage,
            'total_flights': total_flights,
            'total_revenue': float(revenue),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@monitoring_bp.route('/dashboard')
def dashboard():
    """Monitoring dashboard page"""
    return render_template('monitoring_dashboard.html')
