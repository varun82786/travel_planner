from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
import bcrypt
import os
from werkzeug.utils import secure_filename
import certifi
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from scripts.mongoAPI import mongoAPI
from scripts.operationsAPIs import operationsAPI
from scripts.aimodule.prompts import itenaryPrompt, example_json
from scripts.aimodule.geminiai import model
import json
import re

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

        #mongoAPI.travel_db.trips.insert_one(mongoAPI.default_trip(username,operationsAPI.get_date()))

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
            'Title': request.form['Title'],
            'destination': request.form['destination'],
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date'],
            'created_at': operationsAPI.get_date(),
            'updated_at': None,
            'notes': request.form['notes'],
            'checklist': {},  # Use dictionary instead of list
            'expenses': [],
            'files': [],
            "itinerary_used": 0
        }
        mongoAPI.travel_db.trips.insert_one(trip_data)
        flash('Trip added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_trip.html')


@app.route('/edit_trip/<trip_id>', methods=['POST'])
def edit_trip(trip_id):
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    
    if 'Title' not in request.form:
        flash("Error: Title field is missing.", "danger")
        return redirect(url_for('trip_details', trip_id=trip_id))
    
    if 'destination' not in request.form:
        flash("Error: Destination field is missing.", "danger")
        return redirect(url_for('trip_details', trip_id=trip_id))

    updated_trip = {
        'Title': request.form.get('Title', ''),
        'destination': request.form.get('destination', ''),
        'start_date': request.form.get('start_date', ''),
        'end_date': request.form.get('end_date', ''),
        'notes': request.form.get('notes', '')
    }

    mongoAPI.travel_db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": updated_trip}
    )
    
    flash("Trip updated successfully!", "success")
    return redirect(url_for('trip_details', trip_id=trip_id))


@app.route('/trip_details/<trip_id>')
def trip_details(trip_id):
    trip = mongoAPI.travel_db.trips.find_one({'_id': ObjectId(trip_id)})
    
    if not trip:
        flash('Trip not found!', 'danger')
        return redirect(url_for('home'))

    # Ensure checklist is a dictionary with lists
    if 'checklist' not in trip or not isinstance(trip['checklist'], dict):
        trip['checklist'] = {}

    #print("DEBUG: Trip Data ->", trip)  # Check data structure in logs

    return render_template('trip_details.html', trip=trip)

@app.route('/update_trip/<trip_id>', methods=['POST'])
def update_trip(trip_id):
    updated_data = {
        'start_date': request.form['start_date'],
        'end_date': request.form['end_date'],
        'notes': request.form['notes']
    }
    mongoAPI.travel_db.trips.update_one({'_id': ObjectId(trip_id)}, {'$set': updated_data})
    flash('Trip details updated successfully!', 'success')
    return redirect(url_for('trip_details', trip_id=trip_id))

@app.route('/toggle_checklist_item/<trip_id>/<day>/<item_key>', methods=['POST'])
def toggle_checklist_item(trip_id, day, item_key):
    trip = mongoAPI.travel_db.trips.find_one({'_id': ObjectId(trip_id)})
    checklist = trip.get('checklist', {})

    if day in checklist:
        for i in checklist[day]:
            if item_key in i:
                i["completed"] = not i.get("completed", False)

    mongoAPI.travel_db.trips.update_one({'_id': ObjectId(trip_id)}, {'$set': {'checklist': checklist}})
    return redirect(url_for('trip_details', trip_id=trip_id))

@app.route('/trip_overview/<trip_id>')
def trip_overview(trip_id):
    trip = mongoAPI.travel_db.trips.find_one({'_id': ObjectId(trip_id)})
    
    if not trip:
        flash('Trip not found!', 'danger')
        return redirect(url_for('home'))

    return render_template('trip_overview.html', trip=trip)

@app.route('/shared_tripDetail/<trip_id>')
def shared_tripDetail(trip_id):
    trip = mongoAPI.travel_db.trips.find_one({'_id': ObjectId(trip_id)})
    
    if not trip:
        flash('Trip not found!', 'danger')
        return redirect(url_for('home'))
    
    trip = operationsAPI.reset_checklist_completion(trip)
    return render_template('shared_tripDetail.html', trip=trip)

@app.route('/add_to_itinerary/<trip_id>')
def add_to_itinerary(trip_id):
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    # Fetch the shared trip
    trip = mongoAPI.travel_db.trips.find_one({"_id": ObjectId(trip_id), "share": True})
    itinerary_used = trip.get("itinerary_used", 0) + 1
    
    if not trip:
        flash('Trip not found or not shared.', 'danger')
        return redirect(url_for('shared_trips'))

    # Remove MongoDB ObjectId and create a new trip for the logged-in user
    new_trip = {
        "username": session['username'],  # Assign the trip to the logged-in user
        "Title": trip["Title"],
        "destination": trip["destination"],
        "start_date": operationsAPI.get_date(),
        "end_date": operationsAPI.get_date(),
        "created_at": operationsAPI.get_date(),
        "updated_at": None,
        "notes": trip["notes"],
        "checklist": trip.get("checklist", {}),  # Copy checklist if available
        "expenses": trip.get("expenses", []),
        "files": trip.get("files", []),
        "share": False,  # Ensure copied trips are private by default
        "itinerary_used": 0

    }


    new_trip = operationsAPI.reset_checklist_completion(new_trip)
    mongoAPI.travel_db.trips.insert_one(new_trip)  # Save the new trip
    flash('Trip added to your itinerary!', 'success')

    mongoAPI.travel_db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"itinerary_used": itinerary_used}}
    )
    return redirect(url_for('home'))

@app.route('/toggle_share_status/<trip_id>', methods=['POST'])
def toggle_share_status(trip_id):
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    trip = mongoAPI.travel_db.trips.find_one({"_id": ObjectId(trip_id), "username": session['username']})
    if not trip:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('home'))

    # Toggle the share status
    new_share_status = not trip.get("share", False)
    mongoAPI.travel_db.trips.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"share": new_share_status}}
    )

    flash('Trip sharing status updated!', 'success')
    return redirect(url_for('trip_overview', trip_id=trip_id))



@app.route('/add_checklist_item/<trip_id>/<day>', methods=['POST'])
def add_checklist_item(trip_id, day):
    item = request.form['item']
    items_cnt = get_num_items(mongoAPI.travel_db.trips.find_one({'_id': ObjectId(trip_id)}), day)
    mongoAPI.travel_db.trips.update_one(
        {'_id': ObjectId(trip_id)},
        {'$push': {f'checklist.{day}': {f'item{items_cnt}': item, 'completed': False}}}
    )
    return redirect(url_for('trip_details', trip_id=trip_id))

@app.route('/delete_day/<trip_id>/<day>', methods=['POST'])
def delete_day(trip_id, day):
    mongoAPI.travel_db.trips.update_one(
        {'_id': ObjectId(trip_id)},
        {'$unset': {f'checklist.{day}': ""}}
    )
    return redirect(url_for('trip_details', trip_id=trip_id))



@app.route('/edit_checklist_item/<trip_id>/<day>/<item_key>', methods=['POST'])
def edit_checklist_item(trip_id, day, item_key):
    new_item = request.form['new_item']
    trip = mongoAPI.travel_db.trips.find_one({'_id': ObjectId(trip_id)})

    if trip:
        checklist = trip.get('checklist', {})
        if day in checklist:
            for item in checklist[day]:
                if item_key in item:
                    item[item_key] = new_item  # Update the item value

        mongoAPI.travel_db.trips.update_one(
            {'_id': ObjectId(trip_id)},
            {'$set': {'checklist': checklist}}
        )

    return redirect(url_for('trip_details', trip_id=trip_id))



@app.route('/delete_checklist_item/<trip_id>/<day>/<item_key>', methods=['POST'])
def delete_checklist_item(trip_id, day, item_key):
    trip = mongoAPI.travel_db.trips.find_one({'_id': ObjectId(trip_id)})
    
    if trip and 'checklist' in trip and day in trip['checklist']:
        checklist = trip['checklist']
        
        # Remove the dictionary containing the matching key
        checklist[day] = [i for i in checklist[day] if item_key not in i]

        mongoAPI.travel_db.trips.update_one(
            {'_id': ObjectId(trip_id)},
            {'$set': {'checklist': checklist}}
        )

    return redirect(url_for('trip_details', trip_id=trip_id))

@app.route('/add_day/<trip_id>', methods=['POST'])
def add_day(trip_id):
    day = request.form['day']
    mongoAPI.travel_db.trips.update_one({'_id': ObjectId(trip_id)}, {'$set': {f'checklist.{day}': []}})
    return redirect(url_for('trip_details', trip_id=trip_id))


@app.route('/delete_trip/<trip_id>', methods=['POST'])
def delete_trip(trip_id):
    mongoAPI.travel_db.trips.delete_one({"_id": ObjectId(trip_id)})
    flash('Trip deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/shared_trips')
def shared_trips():
    trips = mongoAPI.travel_db.trips.find({"share": True})  # Fetch only shared trips
    return render_template('shared_trips.html', trips=trips)

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

def get_num_items(trip, day):
    return len(trip.get('checklist', {}).get(day, []))

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


# Route to show the AI itinerary form page Route to handle AI itinerary form submission
@app.route('/aigen', methods=['GET','POST'])
def aigen_generate():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        
        trip_details = request.form.get('tripDetails', '')
        print(f"User entered trip details: {trip_details}")
        flash('Trip details received!', 'success')
        flash('Generating itinerary, please wait...', 'info')
        prompt = itenaryPrompt.format(
            example_json=example_json,
            username=session['username'],
            user_description=trip_details
        )


        #print(f"Generated prompt for AI model: {prompt}")
        response = model.generate_content(prompt)
        #print(f"AI model response: {response.text}")
        try:

            # Clean the response text (remove markdown fences if any)
            clean_text = response.text.strip()
            clean_text = re.sub(r"^```(?:json)?", "", clean_text)
            clean_text = re.sub(r"```$", "", clean_text)
            clean_text = clean_text.strip()


            AigenItenary = json.loads(clean_text)
            insertResult = mongoAPI.travel_db.trips.insert_one(AigenItenary)
            trip = mongoAPI.travel_db.trips.find_one({'_id': insertResult.inserted_id}) # Fetch the newly added trip with id to display
            #print(f"Parsed JSON data: {data}")
            return render_template('trip_overview.html', trip=trip)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}\n")
            flash('could not attempt to add itinerary please try again', 'danger')

    return render_template('aigen.html')

# Running the app
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port= 8765)
