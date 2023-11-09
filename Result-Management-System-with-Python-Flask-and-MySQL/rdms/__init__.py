from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from datetime import timedelta
from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, emit
# Initialize flask app
app = Flask(__name__) 
app.config['SECRET_KEY'] = 'secret'
app.config["DEBUG"] = True
CORS(app)

# Set app secret key
# Keep this private!


# Change this URI if you are working with this project on your machine
# Configure database connection 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:laptrinhmangnangcao@laptrinhmangnangcao.cdhsp7ruy5ss.ap-southeast-1.rds.amazonaws.com:3306/project'

# Suppress warnings 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure app to remember user login for 180 seconds on browser terminate
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=180)
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True

# Attach SQLAlchemy to app 
db = SQLAlchemy(app)


from rdms import routes 
