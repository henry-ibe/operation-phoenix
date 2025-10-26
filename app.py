"""
Phoenix Air - Main Application
"""
from flask import Flask, render_template
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
from models import db, Airport, Aircraft, Flight
db.init_app(app)

# Homepage route
@app.route('/')
def index():
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
        result = db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'disconnected: {str(e)}'
    
    return {
        'status': 'healthy',
        'app': 'Phoenix Air',
        'database': db_status
    }

# Register booking blueprint
from routes.booking import booking_bp
app.register_blueprint(booking_bp)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
