from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
import bcrypt
import os
from werkzeug.utils import secure_filename
import certifi
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from scripts.mongoAPI import mongoAPI
from scripts.operationsAPIs import operationsAPI


# Flask app setup
app = Flask(__name__)
#app.config['MONGO_URI'] = uri
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Landing page - Signup or Login
@app.route('/')
def landing():
    return render_template('landing.html')

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Process signup form data and update credentials
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        if mongoAPI.auth_collection.count_documents({'$or': [{'username': username}, {'emailid': email}]}) > 0:
            return render_template('signup.html', error='Username or email already exists.')

        # Add new user credentials
        user_id = operationsAPI.generate_random_string(10)
        user_no = str(mongoAPI.auth_collection.count_documents({}) + 1)
        credentials_data = {
            'unique_id': user_id,
            'username': username,
            'user_no': int(user_no),
            'emailid': email,
            'password': operationsAPI.hash_password(password),
            'privilege': 'normal'
        }
        mongoAPI.auth_collection.insert_one(credentials_data)

        # Redirect to login page
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    global authenticated  # Use the global variable

    if request.method == 'POST':
        # Process login form data and authenticate user
        #credentials_data = operationsAPI.load_credentials_data()
        username = request.form['username']
        password = request.form['password']
        
        user = mongoAPI.auth_collection.find_one({"username": username})
        # Check if username and password match
        if user and operationsAPI.is_password_valid(password,user['password']):
            session['username'] = username  # Store the username in the session
            # Redirect to generator page
            return redirect(url_for('home', trips = mongoAPI.get_trips))

        # Authentication failed, show error message 
        return render_template('login.html', error='Invalid username or password.')

    return render_template('login.html')


# Routes
@app.route('/home')
def home():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    trips = mongoAPI.travel_db.trips.find({"username": session['username']})
    return render_template('home.html', trips=trips)


@app.route('/add_trip', methods=['GET', 'POST'])
def add_trip():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        trip_data = {
            'username': session['username'],  # Associate trip with logged-in user
            'destination': request.form['destination'],
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date'],
            'created_at': operationsAPI.get_date(),
            'updated_at': None,
            'notes': request.form['notes'],
            'checklist': [],
            'expenses': [],
            'files': []
        }
        mongoAPI.travel_db.trips.insert_one(trip_data)
        flash('Trip added successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('add_trip.html')

@app.route('/edit_trip/<trip_id>', methods=['GET', 'POST'])
def edit_trip(trip_id):
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    trip = mongoAPI.travel_db.trips.find_one({"_id": ObjectId(trip_id), "username": session['username']})
    if not trip:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        updated_trip = {
            'destination': request.form['destination'],
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date'],
            'updated_at': operationsAPI.get_date(),
            'notes': request.form['notes'],
            
        }
        mongoAPI.travel_db.trips.update_one({"_id": ObjectId(trip_id), "username": session['username']}, {"$set": updated_trip})
        flash('Trip updated successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('edit_trip.html', trip=trip)


@app.route('/delete_trip/<trip_id>', methods=['POST'])
def delete_trip(trip_id):
    mongoAPI.travel_db.trips.delete_one({"_id": ObjectId(trip_id)})
    flash('Trip deleted successfully!', 'success')
    return redirect(url_for('home'))

# Template for handling uploads (photos/tickets)
@app.route('/upload/<trip_id>', methods=['POST'])
def upload_file(trip_id):
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    mongoAPI.travel_db.trips.update_one({"_id": trip_id}, {"$push": {"files": filename}})
    flash('File uploaded successfully!', 'success')
    return redirect(url_for('home'))

# Utility functions for CRUD operations (optional based on your needs)
def create_document(collection, data):
    try:
        result = collection.insert_one(data)
        print(f"Inserted document with ID: {result.inserted_id}")
    except Exception as e:
        print("Error creating document:", e)

def read_documents(collection, filter_query=None):
    try:
        documents = collection.find(filter_query) if filter_query else collection.find()
        return documents
    except Exception as e:
        print("Error reading documents:", e)
        return []

# Running the app
if __name__ == '__main__':
    app.run(debug=True)
