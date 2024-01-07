from configs.config import *
import requests
import json
import os
import uuid
from utils.db_tools import save_users , get_user_from_database
from utils.tools import *
import logging
logging.basicConfig(filename='api.log', level=logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logging.getLogger('').addHandler(console_handler)



def login_and_get_cookie(panel_domain)-> dict:
    ses = requests.Session()
    data = {"username": panel_username , "password": panel_password}
    url = f"{panel_domain}/login"
    response = ses.post(url, data=data)
    if response.status_code == 200:
        return response.cookies.get_dict()
    logging.error("Error response: %s", f"failed to login {url}")
    return None


def store_panels_login_sessions():
    list_of_panels = []
    
    try:
        if not os.path.exists('users.json'):
            save_users()
        with open('users.json', 'r') as file:
            json_content = file.read()
        data = json.loads(json_content)
        panel_domains = set("http://"+entry["panel_domain"]+"."+panel_suffix+":2053" for entry in data)
        list_of_panels = list(panel_domains)
    except Exception as e :
        logging.error('[X] Error extracting panels : {}'.format(e)) 
    sessions = {}
    for panel in list_of_panels :
        sessions[panel.split('//')[1].split('.')[0]] = login_and_get_cookie(panel)

    with open('sessions.json','w') as f:
        json.dump(sessions,f)
        print('panels session logins saved')
        
def get_panel_session(panel_domain):
    print(panel_domain)
    print('panel domain ------------>'+panel_domain.split('//')[1].split('.')[0])
    if not os.path.exists('sessions.json'):
        store_panels_login_sessions()  
    with open('sessions.json','r') as f :
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
       logging.error("Error response: %s", f"failed to get client data becaouse {e}") 
    



def delete_client(email,panel_domain,inbound_id):
    cookie =get_panel_session(panel_domain)
    try:
        url = '{}/panel/api/inbounds/{}/delClient/{}'.format(panel_domain,inbound_id,get_user_from_database(email)['uuid'])
        print(url)
        headers = {'Accept': 'application/json',
                "Cookie": "; ".join([f"{k}={v}" for k, v in cookie.items()])}
        
        ses = requests.Session()
        response = ses.post(url,headers=headers)
        print(response.content)
        
        
        result = json.loads(response.content)['success']
    
        if response.status_code==200 and result==True:
            logging.info("[✓] result : user with email [{}] deleted ".format(email))  
        else:
            logging.error("[X] result : user with email [{}] not deleted [{}]".format(email,response.content)) 
    except Exception as e :
        logging.error('failed deleting user [{}]'.format(e))
                       
        
                
                
def get_uuids(panel_domain)-> dict:
    try:
        clients_data = get_client_data(panel_domain)
        settings = {}
        uuids = {}
        for obj in clients_data['obj']:
            settings = obj['settings']
        settings = json.loads(settings)
        for user in settings['clients']:
            email = user['email']
            uuid = user['id']
            uuids[email] = uuid
           

        return uuids

    except Exception as e:
        logging.error('Getting panels users UUID failed: {}'.format(e))
        return {}



def get_user_old_data(panel_domain, email):
    try:
        data = get_client_data(panel_domain=panel_domain)
        for obj in data['obj']:
            if obj['clientStats']:
                clients = obj['clientStats']
                for client in clients:
                    if client['email'] == email:
                        email = client['email']
                        traffic = client['total']
                        expire_date = client['expiryTime']
                        usage = client['down'] + client['up']
                        list_uuids = get_uuids(panel_domain=panel_domain)
                        if traffic == 0:
                            user_uuid = list_uuids[email]
                            traffic = 214748364800 - usage
                        else:
                            user_uuid = list_uuids[email]
                            traffic = traffic - usage

                        return {'traffic': traffic, 'expire': expire_date, 'user_uuid': user_uuid}
        logging.info('User {} not found to get previous data'.format(email))

    except Exception as e:
        logging.error("Getting user's previous data failed: {}".format(e))
    return None
           
                            
                                        
     
def add_client(inbound_id, email, traffic, expire_days, panel_domain)->str:
    try:
        user_uuid = str(uuid.uuid4())
        cookie =get_panel_session(panel_domain)
        url = '{}/panel/api/inbounds/addClient'.format(panel_domain)
        headers = {'Accept': 'application/json',
                   "Cookie": "; ".join([f"{k}={v}" for k, v in cookie.items()])}
        traffic = gb_to_bytes(traffic)
        expire_days = days_to_timestamp(expire_days) * 1000
        data_payload = {
            "id": inbound_id,
            "settings": "{\"clients\":[{\"id\":\"" + user_uuid +
                        "\",\"alterId\":0,\"email\":\"" + email +
                        "\",\"limitIp\":0,\"totalGB\":" + str(traffic) +
                        ",\"expiryTime\":" + str(int(expire_days)) +
                        ",\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}]}"
        }
        ses = requests.Session()
        response = ses.post(url, headers=headers, data=data_payload)
        print(response.content)
        result = json.loads(response.content)['success']
        if response.status_code == 200 and result:
            logging.info("[✓] Result: User with email {} added".format(email))
            return user_uuid
        else:
            logging.error("[X] Result: User with email {} not added [{}]".format(email, response.content))

    except Exception as e:
        logging.error("Creating new user in the X-UI panel failed [{}]".format(e))



            
def update_existing_user_traffic(email, traffic, panel_domain, inbound_id)->None:
    try:
        user_uuid = get_user_from_database(email)['uuid']

        cookie =get_panel_session(panel_domain)
        url = '{}/panel/api/inbounds/updateClient/{}'.format(panel_domain, user_uuid)
        headers = {'Accept': 'application/json',
                   "Cookie": "; ".join([f"{k}={v}" for k, v in cookie.items()])}

        data = get_client_data(panel_domain=panel_domain)
        old_expire_date = 0
        for obj in data['obj']:
            if obj['clientStats']:
                clients = obj['clientStats']
                for client in clients:
                    if client['email'] == email:
                        old_expire_date = client['expiryTime']
        traffic = gb_to_bytes(traffic)
        data_payload = {
            "id": inbound_id,
            "settings": "{\"clients\":[{\"id\":\"" + user_uuid +
                        "\",\"alterId\":0,\"email\":\"" + email +
                        "\",\"limitIp\":0,\"totalGB\":" + str(traffic) +
                        ",\"expiryTime\":" + str(old_expire_date) +
                        ",\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}]}"
        }
        ses = requests.Session()
        response = ses.post(url, headers=headers, data=data_payload)
        result = json.loads(response.content)['success']
        if response.status_code == 200 and result:
            logging.info("Updating User [{}] Traffic in X-UI Panel Successful".format(email))
        else:
            logging.error("Updating User [{}] Traffic in X-UI Panel Failed [{}]".format(email, response.content))

    except Exception as e:
        logging.error("Updating User Traffic in X-UI Panel Failed [{}]".format(e))



def update_existing_user_expire_date(email, expire_days, panel_domain, inbound_id)->None:
    try:
        user_uuid = get_user_from_database(email)['uuid']
        cookie =get_panel_session(panel_domain)
        url = '{}/panel/api/inbounds/updateClient/{}'.format(panel_domain, user_uuid)
        headers = {'Accept': 'application/json',
                   "Cookie": "; ".join([f"{k}={v}" for k, v in cookie.items()])}

        data = get_client_data(panel_domain=panel_domain)

        old_traffic = 0
        for obj in data['obj']:
            if obj['clientStats']:
                clients = obj['clientStats']
                for client in clients:
                    if client['email'] == email:
                        old_traffic = client['total']

        expire_days = days_to_timestamp(expire_days) * 1000

        data_payload = {
            "id": inbound_id,
            "settings": "{\"clients\":[{\"id\":\"" + user_uuid +
                        "\",\"alterId\":0,\"email\":\"" + email +
                        "\",\"limitIp\":0,\"totalGB\":" + str(old_traffic) +
                        ",\"expiryTime\":" + str(expire_days) +
                        ",\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}]}"
        }

        ses = requests.Session()
        response = ses.post(url, headers=headers, data=data_payload)
        result = json.loads(response.content)['success']
        if response.status_code == 200 and result:
            logging.info("Updating User [{}] ExpireDays in X-UI Panel Successful".format(email))
        else:
            logging.error("Updating User [{}] ExpireDays in X-UI Panel Failed [{}]".format(email, response.content))

    except Exception as e:
        logging.error("Updating User ExpireDays in X-UI Panel Failed [{}]".format(e))


def update_existing_user_traffic_expiredays(email, inbound_id, traffic, expire_days, panel_domain)->None:
    try:
        user_uuid = get_user_from_database(email)['uuid']
        print(expire_days)
        cookie =get_panel_session(panel_domain)
        url = '{}/panel/api/inbounds/updateClient/{}'.format(panel_domain, user_uuid)
        headers = {'Accept': 'application/json',
                   "Cookie": "; ".join([f"{k}={v}" for k, v in cookie.items()])}
        traffic = gb_to_bytes(traffic)
        expire_days = days_to_timestamp(int(expire_days)) * 1000
        data_payload = {
            "id": inbound_id,
            "settings": "{\"clients\":[{\"id\":\"" + user_uuid +
                        "\",\"alterId\":0,\"email\":\"" + email +
                        "\",\"limitIp\":0,\"totalGB\":" + str(traffic) +
                        ",\"expiryTime\":" + str(expire_days) +
                        ",\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}]}"
        }
        ses = requests.Session()
        response = ses.post(url, headers=headers, data=data_payload)
        result = json.loads(response.content)['success']
        if response.status_code == 200 and result:
            logging.info("Updating User [{}] Traffic and ExpireDays in X-UI Panel Successful".format(email))
        else:
            logging.error("Updating User [{}] Traffic and ExpireDays in X-UI Panel Failed [{}]".format(email, response.content))

    except Exception as e:
        logging.error("Updating User Traffic and ExpireDays in X-UI Panel Failed [{}]".format(e))



def get_user_info(email, panel_domain):
    cookie =get_panel_session(panel_domain)
    print(cookie)
    try:
        header = {
            "Accept": "application/json",
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookie.items()])
        }
        url = f"{panel_domain}/panel/api/inbounds/getClientTraffics/{email}"
        ses = requests.Session()
        response = ses.get(url, headers=header)
        print(response.content)
        data = json.loads(response.content)
        
        if data['obj']['expiryTime']==0:
            expire_time=0
        else:    
            
            expire_time = timestamp_to_jalali(data['obj']['expiryTime']).split(' ')[0] + ' ' + iranian_months[
            timestamp_to_jalali(data['obj']['expiryTime']).split(' ')[1].lower()]
        if data['obj']['total']==0:
            total=0
        else:    
            total = bytes_to_gb_mb(data['obj']['total'])
        used = bytes_to_gb_mb(data['obj']['up'] + data['obj']['down'])
        status =data['obj']['enable'] 
        if status==True:
            status='Active'
        else:
            status='Deactive'    
        inbound_id = data['obj']['inboundId']

        return {
            "name" : email,
            "inboundId": inbound_id,
            "usage": used,
            "total": total,
            "expire": expire_time,
            "days": date_difference_in_days(data['obj']['expiryTime']),
            "expirets":data['obj']['expiryTime'],
            "totalbyte":data['obj']['total'],
            "upbyte":data['obj']['up'],
            'dlbyte':data['obj']['down'],
            "usagebyte":data['obj']['up'] + data['obj']['down'],
            "expjl":meow_jalali(data['obj']['expiryTime']),
            "status" : status
            }
    except Exception as e:
        logging.error("Getting User Data from Xui Panel Failed [{}] ".format(e))    

            
            
