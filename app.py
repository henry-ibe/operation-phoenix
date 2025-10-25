"""
Phoenix Air - Main Application
Connected to PostgreSQL Database
"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Airport Model (matches our database table)
class Airport(db.Model):
    __tablename__ = 'airports'
    airport_code = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    timezone = db.Column(db.String(50))

# Aircraft Model
class Aircraft(db.Model):
    __tablename__ = 'aircraft'
    aircraft_id = db.Column(db.Integer, primary_key=True)
    registration = db.Column(db.String(10))
    model = db.Column(db.String(50))
    total_seats = db.Column(db.Integer)
    economy_seats = db.Column(db.Integer)
    business_seats = db.Column(db.Integer)
    first_class_seats = db.Column(db.Integer)

# Homepage route - show real data from database!
@app.route('/')
def index():
    # Get airports from database
    airports = Airport.query.all()
    aircraft = Aircraft.query.all()
    
    return render_template('index.html', 
                         app_name='Phoenix Air',
                         airports=airports,
                         aircraft=aircraft)

# Health check
@app.route('/health')
def health():
    try:
        # Test database connection
        result = db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'disconnected: {str(e)}'
    
    return {
        'status': 'healthy',
        'app': 'Phoenix Air',
        'database': db_status
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
