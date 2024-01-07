import json
import os

import json
import requests 
from datetime import datetime
from configs.config import panel_username , panel_password
from utils.xui_utils import get_client_data
import os
from utils.db_tools import save_users

if not os.path.exists('users.json'):
        save_users()
with open('users.json','r') as f :
    users = json.load(f)
    
  
  

with open('users.json','r') as f :
    users = json.load(f)
    
    
def extract_panel_domains():
    if not os.path.exists('users.json'):
        save_users()
    with open('users.json', 'r') as file:
        json_content = file.read()
    data = json.loads(json_content)
    panel_domains = set(entry["panel_domain"] for entry in data)
    return list(panel_domains)






def login_and_get_cookie(panel_domain)-> dict:
    """
    Authenticates the user with the X-UI panel and returns the session cookie.

    Parameters:
    - panel_domain (str): The domain of the X-UI panel.

    Returns:
    - dict or None: A dictionary containing the session cookie if authentication is successful,
      otherwise returns None.
    """
    ses = requests.Session()
    data = {"username": panel_username, "password": panel_password}
    url = f"{panel_domain}/login"
    
    response = ses.post(url, data=data)
    
    if response.status_code == 200:
        
        return response.cookies.get_dict()
    return None


    
    

def days_difference_from_timestamp(timestamp):
    dt_object = datetime.fromtimestamp(timestamp / 1000.0)  # Assuming the timestamp is in milliseconds
    current_datetime = datetime.now()
    time_difference = dt_object - current_datetime
    days_difference = time_difference.days
    return days_difference
    
    
def dump_panel(panel_domain):
    print('[*] dumping {} paneldata to file '.format(panel_domain))
    data = get_client_data(cookie=login_and_get_cookie(panel_domain),panel_domain=panel_domain)
    data_to_save = {}
    for obj in data['obj']:
        if obj['clientStats']:
            clients = obj['clientStats']
            for client in clients :
                traffic_alert = False
                expire_alert= False
                username = client['email']
                traffic = client['total']-(client['down']+client['up'])
                expire_days = days_difference_from_timestamp(client['expiryTime'])
                user_status=  client['enable']
                if traffic!=0 and traffic<3 :
                    traffic_alert = True
                if expire_days>0 and expire_days<3:
                    expire_alert = True    
                data_to_save[username] = {
                    'username' : username,
                    'status' : user_status,
                    'remaining_days' :expire_days,
                    'remaining_traffic' : int(traffic / (1024 ** 3)),
                    "traffic_alert" : traffic_alert,
                    "expire_alert" : expire_alert
                }
    with open('panels_dump/'+panel_domain.split('/')[-1].split(':')[0].split('.')[0]+'.json','w') as f:
        json.dump(data_to_save,f) 
        print('dumping data to file done')          

def dump_panels():              
    for panel in extract_panel_domains():
        try:
            dump_panel(panel_domain=panel)
        except:
            continue    
        
        

    
def get_users_services(user_id):
    print(user_id)
    ls = []
    services={}
    print('[*] getting users services')
    for user in users:
        try:
            
            if str(user['_id'].split('-')[0])==str(user_id):
                services[user['_id']]=user['panel_domain'].split('/')[-1].split(':')[0].split('.')[0]
        except Exception as e :
           print(e)   
        
    for service in services:
        try:
            if os.path.exists('panels_dump/{}'.format(services[service])) :
                dump_panels()
            with open('panels_dump/{}.json'.format(services[service])) as f :
                data = json.load(f)     
        except Exception as e :
            print(e)        
    
    
    for user in data :
      if user.split('-')[0]==user_id:
        ls.append(data.get(user))     
      
    return ls  
    
