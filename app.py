"""
Phoenix Air - Main Application
A simple airline booking system
"""

from flask import Flask, render_template
import os

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-later'

# Homepage route
@app.route('/')
def index():
    return render_template('index.html', 
                         app_name='Phoenix Air',
                         message='Welcome to Phoenix Air!')

# Health check
@app.route('/health')
def health():
    return {'status': 'healthy', 'app': 'Phoenix Air'}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
