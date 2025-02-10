import sys
sys.path.append(r'scripts')

from mongoAPI import mongodb_init 
#import mongodb_init
import bcrypt

Client = mongodb_init.server_check()

# Replace "your_collection_name" with the name of your desired collection
auth_collection = Client["travel"]["auth"]
hashtag_collection = Client["travel"]["trips"]
travel_db = Client["travel"]



# sign up and login operations

def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def is_password_valid(entered_password, stored_hashed_password):
    # Check if the entered password matches the stored hashed password
    return bcrypt.checkpw(entered_password.encode('utf-8'), stored_hashed_password)

def signup_user(user_data):
    # Check if username already exists
    # existing_user = auth_collection.find_one({"username": user_data["username"]})
    # if existing_user:
    #     return "Username already exists"
    
    # Hash the password before storing it
    # hashed_password = hash_password(user_data["password"])
    # user_data["password"] = hashed_password
    
    # Insert the new user data
    result = auth_collection.insert_one(user_data)
    return "User signed up successfully"

def login_user(username, password):
    user = auth_collection.find_one({"username": username})
    if not user:
        return "User not found"
    
    if is_password_valid(password, user["password"]):
        return "Login successful"
    else:
        return "Incorrect password"


# CRUD Operations

def create_document(collection, data):
    try:
        result = collection.insert_one(data)
        print(f"Inserted document with ID: {result.inserted_id}")
    except Exception as e:
        print("Error creating document:", e)

def read_documents(collection, filter_query=None):
    try:
        documents = collection.find(filter_query) if filter_query else collection.find()
        for doc in documents:
            print(doc)
        return documents
    except Exception as e:
        print("Error reading documents:", e)

def update_document(collection, filter_query, update_data):
    try:
        result = collection.update_one(filter_query, {"$set": update_data})
        print(f"Modified {result.modified_count} document(s).")
    except Exception as e:
        print("Error updating document:", e)

def delete_document(collection, filter_query):
    try:
        result = collection.delete_one(filter_query)
        print(f"Deleted {result.deleted_count} document.")
    except Exception as e:
        print("Error deleting document:", e)

def doc_details(collection= hashtag_collection,hashtag="None"):
    result = collection.find_one({"hashtag": hashtag}, {"category": 1, "gener": 1, "location": 1, "parameters": 1})
    #print(result)
    return result

# lis = ["skyphotography", "worldphotographyday" ,"ballaratphoto" ,"officialphotographyhub" ,"traveldiary" ,"thephotographyblogger"  ]

# for hash in lis:
#     print(doc_details(hashtag_collection,hash))

#read_documents(auth_collection)

def get_trips():

    trips = travel_db.trips.find()

    return trips


def default_trip(username, created_date):
    default_data = {
        "username": f"{username}",
        "destination": "Varanasi (3-Day Spiritual & Cultural Escape)",
        "start_date": f"{created_date}",
        "end_date": f"{created_date}",
        "created_at": f"{created_date}",
        "updated_at": None,
        "notes": "Immerse in the mysticism and energy of the oldest living city!",
        "checklist": {
            "Day 1": [
                {"item0": "Arrive in Varanasi and check in to a heritage guesthouse by the Ganges.", "completed": False},
                {"item1": "Stroll through the narrow alleys of the Old City and soak in the chaos.", "completed": True},
                {"item2": "Visit the sacred Kashi Vishwanath Temple – feel the divine vibrations.", "completed": False},
                {"item3": "Take a mesmerizing sunset boat ride on the Ganges.", "completed": False},
                {"item4": "Witness the spellbinding Ganga Aarti at Dashashwamedh Ghat.", "completed": False},
                {"item5": "Indulge in street food: Try the famous Banarasi chaat & malaiyyo.", "completed": False}
            ],
            "Day 2": [
                {"item0": "Wake up early for a serene sunrise boat ride along the ghats.", "completed": False},
                {"item1": "Explore the eerie Manikarnika Ghat, where life and death intertwine.", "completed": False},
                {"item2": "If visiting during Holi, experience the Masan Holi with Aghori sadhus.", "completed": False},
                {"item3": "Visit Sarnath, the land of Buddha’s first sermon.", "completed": False},
                {"item4": "Discover local markets for Banarasi silk sarees and souvenirs.", "completed": False},
                {"item5": "Enjoy a soulful evening music performance at a local haveli.", "completed": False}
            ],
            "Day 3": [
                {"item0": "Attend a peaceful morning yoga session on Assi Ghat.", "completed": False},
                {"item1": "Visit hidden gems like Nepali Temple & Kedar Ghat.", "completed": False},
                {"item2": "Have a final cup of Banarasi chai with river views.", "completed": False},
                {"item3": "Say goodbye to the magical city and depart with your heart full of memories.", "completed": False}
            ]
        },
        "share": False,
        "expenses": [],
        "files": []
    }
    
    return default_data

def update_all_documents(collection, update_data):
    try:
        result = collection.update_many({}, {"$set": update_data})
        print(f"Modified {result.modified_count} document(s).")
    except Exception as e:
        print("Error updating documents:", e)

# Example usage:
#update_all_documents(travel_db.trips, {"share": False})