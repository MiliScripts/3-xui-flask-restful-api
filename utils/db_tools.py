# Import necessary modules and libraries
import os
import pymongo
import json
from json import dumps
from configs.config import *

client = pymongo.MongoClient(mongo_string)
db = client['api']
users_collection = db["users"]


def show_users():
    user_ids = [x['_id'] for x in users_collection.find({})]
    return user_ids


def delete_user_from_database(username):
    
    users_collection.delete_one({'_id': username})
    save_users()
    return True


def read_users():
    if not os.path.exists('users.json'):
        save_users()
    with open('users.json', 'r') as file:
        data = json.load(file)
    return data


def save_users():
    cursor = users_collection.find()
    document_list = list(cursor)
    json_data = dumps(document_list)
    with open(os.path.join('users.json'), 'w') as file:
        file.write(json_data)




def get_user_from_database(username):
    for user in read_users():
        if user['_id'] == username:
            return user
    return 'User Not Found'


