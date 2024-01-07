import json
# Import necessary modules and libraries
import os
import pymongo
from datetime import datetime
import json
import requests
import schedule
from json import dumps
panel_password = 'devVpn100%'
panel_username = 'devVpn'
panel_suffix = 'whitemeow.site'
panel_port = '2053'
config_port ='80'
mongo_string = 'mongodb+srv://mili:mili@cluster0.tz6xsvm.mongodb.net/?retryWrites=true&w=majority'


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
    if not os.path.exists('3-xui-flask-restful-api/users.json'):
        save_users()
    with open('3-xui-flask-restful-api/users.json', 'r') as file:
        data = json.load(file)
    return data


def save_users():
    cursor = users_collection.find()
    document_list = list(cursor)
    json_data = dumps(document_list)
    with open(os.path.join('3-xui-flask-restful-api/users.json'), 'w') as file:
        file.write(json_data)




def get_user_from_database(username):
    for user in read_users():
        if user['_id'] == username:
            return user
    return 'User Not Found'


def format_panel_domain(panel_domain):
    return f'http://{panel_domain}.{panel_suffix}:{panel_port}'


def login_and_get_cookie(panel_domain)-> dict:
    ses = requests.Session()
    data = {"username": panel_username , "password": panel_password}
    url = f"{panel_domain}/login"
    response = ses.post(url, data=data)
    if response.status_code == 200:
        return response.cookies.get_dict()
    
    return None


def store_panels_login_sessions():
    list_of_panels = []
    
    try:
        if not os.path.exists('3-xui-flask-restful-api/users.json'):
            save_users()
        with open('3-xui-flask-restful-api/users.json', 'r') as file:
            json_content = file.read()
        data = json.loads(json_content)
        panel_domains = set("http://"+entry["panel_domain"]+"."+panel_suffix+":2053" for entry in data)
        list_of_panels = list(panel_domains)
    except Exception as e :
        pass
    sessions = {}
    for panel in list_of_panels :
        sessions[panel.split('//')[1].split('.')[0]] = login_and_get_cookie(panel)

    with open('3-xui-flask-restful-api/sessions.json','w') as f:
        json.dump(sessions,f)
        print('panels session logins saved')
        
def get_panel_session(panel_domain):
    print(panel_domain)
    print('panel domain ------------>'+panel_domain.split('//')[1].split('.')[0])
    if not os.path.exists('3-xui-flask-restful-api/sessions.json'):
        store_panels_login_sessions()  
    with open('3-xui-flask-restful-api/sessions.json','r') as f :
        sessions = json.load(f)
        panel_domain = panel_domain.split('//')[1].split('.')[0]
        if  panel_domain in sessions:
            return sessions[panel_domain]   
        
             

def get_client_data(panel_domain)-> dict:
    cookie = get_panel_session(panel_domain)
    try:
        header = {
            "Accept": "application/json",
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookie.items()])
        }
        url = f"{panel_domain}/panel/api/inbounds/list"
        ses = requests.Session()
        response = ses.get(url, headers=header)
        data = json.loads(response.content)
        # print(data)
        return data
    except Exception as e :
       pass
    

#update panel_dumps
with open('3-xui-flask-restful-api/users.json','r') as f :
    users = json.load(f)
    
    
def extract_panel_domains():
    try:
        if not os.path.exists('3-xui-flask-restful-api/users.json'):
            save_users()
        with open('3-xui-flask-restful-api/users.json', 'r') as file:
            json_content = file.read()
        data = json.loads(json_content)
        panel_domains = set(format_panel_domain(entry["panel_domain"]) for entry in data)
        
        return list(panel_domains)
    
    except Exception as e :
        pass




def days_difference_from_timestamp(timestamp):
    if timestamp==0 or timestamp<0:
        return 0
    print(timestamp)
    dt_object = datetime.fromtimestamp(timestamp / 1000.0)  # Assuming the timestamp is in milliseconds
    current_datetime = datetime.now()
    time_difference = dt_object - current_datetime
    days_difference = time_difference.days
    return days_difference
    
    
def dump_panel(panel_domain):
    data = get_client_data(panel_domain=panel_domain)
    data_to_save = {}
    try:
        for obj in data['obj']:
            if obj['clientStats']:
                clients = obj['clientStats']
                for client in clients :
                    
                    username = client['email']
                    if client['total']==0:
                       traffic = client['total']-(client['down']+client['up'])
                    else:
                       traffic = client['total']-(client['down']+client['up'])    
                    expire_days = days_difference_from_timestamp(client['expiryTime'])
                    user_status=  client['enable']        
                    data_to_save[username] = {
                        'username' : username,
                        'total_traffic':int(client['total'] / (1024 ** 3)),
                        'panel': panel_domain,
                        'status' : user_status,
                        'remaining_days' :expire_days,
                        'remaining_traffic' : int(traffic / (1024 ** 3)),
                    }
        with open('3-xui-flask-restful-api/panels_dump/'+panel_domain.split('/')[-1].split(':')[0].split('.')[0]+'.json','w') as f:
            json.dump(data_to_save,f) 
             
            return
    except Exception as e :
        pass    

def dump_panels():      
    
    dumped_panels = []    
    failed_panels = []    
    for panel in extract_panel_domains():
        try:
            dump_panel(panel_domain=panel)
            dumped_panels+=panel.split('/')[-1].split(':')[0].split('.')[0]
        except Exception as e :
            failed_panels+=panel.split('/')[-1].split(':')[0].split('.')[0]
            continue

            
                        
            
save_users()
store_panels_login_sessions()
dump_panels()
