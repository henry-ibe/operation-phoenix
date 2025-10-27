"""
Authentication Routes - Login, Register, Logout
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Booking
from datetime import datetime

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            created_at=datetime.now()
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log user in
        login_user(user)
        flash(f'Welcome to Phoenix Air, {first_name}!', 'success')
        
        return redirect(url_for('auth.dashboard'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - view all bookings"""
    # Get user's bookings
    bookings = Booking.query.filter_by(user_id=current_user.user_id).order_by(Booking.booking_date.desc()).all()
    
    return render_template('auth/dashboard.html', bookings=bookings)

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Get user stats
    total_bookings = Booking.query.filter_by(user_id=current_user.user_id).count()
    checked_in_bookings = Booking.query.filter_by(user_id=current_user.user_id, checked_in=True).count()
    
    return render_template('auth/profile.html', 
                         total_bookings=total_bookings,
                         checked_in_bookings=checked_in_bookings)

@auth_bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    
    current_user.first_name = first_name
    current_user.last_name = last_name
    current_user.phone = phone
    
    db.session.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))
