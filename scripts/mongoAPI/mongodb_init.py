from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from urllib.parse import quote_plus

# Replace <username> and <password> with your actual MongoDB Atlas credentials
username = "edith"
password = "varun82786"
database_name = "travel"  # Replace with the name of your desired database

# Local MongoDB (destination)
local_username = "varun"
local_password = "Varun@82786"
local_host = "192.168.31.145"
local_port = 9638

# Construct the MongoDB connection URI
uri = f"mongodb://{quote_plus(local_username)}:{quote_plus(local_password)}@{local_host}:{local_port}/"

# Create a new client and connect to the server
def server_check():
    client = MongoClient(uri)
    try:
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!\n")
        return client
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        return None

# Call the function to test the connection
#client = server_check()

#server_check()

# Now you can use the 'client' object to interact with your MongoDB deployment
# For example, you can access databases and collections as follows:
# db = client[database_name]
# collection = db["your_collection_name"]
# collection.insert_one({"key": "value"})

# Don't forget to close the connection when you're done
#if client:
#    client.close()
