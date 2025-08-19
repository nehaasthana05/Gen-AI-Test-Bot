import sys
from werkzeug.security import check_password_hash
from pymongo import MongoClient

hostname = '130.113.68.57'  # Update to the server's IP address
port = 27017
database_name = 'genAI'

uri = f'mongodb://{hostname}:{port}/{database_name}'
try:
    client = MongoClient(uri)
except Exception as e:
    print(f"Error: Connection failed {e}")
    raise Exception

db = client[database_name]
users_collection = db["users"]

email = sys.argv[1]
password = sys.argv[2]

user = users_collection.find_one({'email': email})

if not user:
    print("Error: User not found")
elif not check_password_hash(user['password'], password):
    print("Error: Incorrect password")
else:
    user_id = str(user['_id'])
    print(user_id)