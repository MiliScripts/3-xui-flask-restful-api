import urllib.parse
import requests
import json
import logging
from configs.config import *
import pymongo
from utils.tools import generate_unique_token
from utils.tools import format_panel_domain
from utils.xui_utils import get_panel_session , get_user_old_data , get_user_info ,add_client, update_existing_user_traffic, update_existing_user_traffic_expiredays, update_existing_user_expire_date, delete_client
from utils.db_tools import  get_user_from_database, save_users, delete_user_from_database, users_collection, read_users
import os

def add_user(username, panel_domain, flag, inbound_id, traffic, expire_days):
    logging.info(f'[*] Adding user {username} to {panel_domain}')
    try:
        subscription_token = generate_unique_token()
        new_user_uuid = add_client(
            email=username,
            panel_domain=format_panel_domain(panel_domain),
            traffic=traffic,
            expire_days=expire_days,
            inbound_id=inbound_id
        )

        user = {
            '_id': username,
            'uuid': new_user_uuid,
            "panel_domain": panel_domain.split('.')[0],
            "sub": f'{sub_host_url}/sub/{subscription_token}',
            "token": subscription_token,
            "flag": flag
        }

        users_collection.insert_one(user)
        save_users()
        logging.info(f'[✓] User {username} added to {format_panel_domain(panel_domain)} panel')
        return f'{sub_host_url}/sub/{subscription_token}'

    except pymongo.errors.DuplicateKeyError:
        logging.error('Failed to add new user to MongoDB')
        return "User already exists"
    except Exception as e:
        logging.error(f'Failed to add new user [{e}]')


def update_user(username, panel_domain, sub_change, flag, inbound_id=None, traffic=None, expire_days=None):
    panel_domain = format_panel_domain(panel_domain)
    logging.info(f'[*] Updating user {username}')

    try:
        existing_user = users_collection.find_one({"_id": username})

        if sub_change == "true":
            new_subscription_token = generate_unique_token()
            updated_user = {
                '_id': username,
                "uuid": get_user_from_database(username)['uuid'],
                "panel_domain": panel_domain.split("//")[1].split('.')[0],
                "sub": f'{sub_host_url}/sub/{new_subscription_token}',
                "token": new_subscription_token,
                "flag": flag
            }
        else:
            current_subscription_token = existing_user.get('sub', '')
            updated_user = {
                '_id': username,
                "uuid": get_user_from_database(username)['uuid'],
                "panel_domain": panel_domain.split("//")[1].split('.')[0],
                "token": current_subscription_token.split('/')[-1],
                "sub": current_subscription_token,
                "flag": flag
            }

        if inbound_id and traffic is not None:
            update_existing_user_traffic_expiredays(
                email=username,
                inbound_id=inbound_id,
                traffic=traffic,
                expire_days=expire_days,
                panel_domain=panel_domain
            )
        elif traffic is not None:
            update_existing_user_traffic(
                email=username,
                traffic=traffic,
                panel_domain=panel_domain,
                inbound_id=inbound_id,
            )
            logging.info(f"[✓] User {username} traffic updated")
            return "User traffic updated"

        elif expire_days is not None:
            update_existing_user_expire_date(
                email=username,
                expire_days=expire_days,
                panel_domain=panel_domain,
                inbound_id=inbound_id,
            )
            logging.info(f"[✓] User {username} expire days updated")
            return f"User {username} expire days updated"

        users_collection.delete_one({'_id': username})
        users_collection.insert_one(updated_user)
        save_users()
        return updated_user.get('sub', '')

    except Exception as e:
        logging.error(f"[Error] Updating user: {e}")
        return f"Error updating user: {e}"


def generate_subscription_status_config(username, panel_domain):
    logging.info(f'---> [*] Generating user {username} subscription info')

    user_info = get_user_info(email=username, panel_domain=panel_domain)
    null_domain = panel_domain.split('//')[1].split(':')[0]
    meow = f"""#profile-title: {user_info['name']}
#profile-update-interval: 1
#subscription-userinfo: upload={user_info['upbyte']}; download={user_info['dlbyte']}; total={user_info['totalbyte']}; expire={str(int(user_info['expirets']/1000))}
"""
    v2_temp = 'vless://{}@{}:8080?type=tcp&security=reality&fp=firefox&pbk=lxERA2lBP2A7popq8zO3edLMPaVeLaCqxKhsXT9H6Qs&sni=www.speedtest.net&sid=4182ee67&spx=%2F#{}'
    status_config = '{}' + '\n' + v2_temp.format(
        null_domain, null_domain, urllib.parse.quote(f'ترافیک {user_info["usage"]} از {user_info["total"]}* انقضا {user_info["expire"]}'))
    extra_info = {
        'user_name': user_info['name'],
        'total_usage': user_info['total'],
        'usage': user_info['usage'],
        'expire_date': user_info['expjl'],
        'total_byte': user_info['totalbyte'],
        'usage_byte': user_info['usagebyte'],
        'remainig_days': user_info['days'],
        'status': user_info['status']
    }
    text = meow + '\n' + status_config
    logging.info(f'---> [✓] User {username} subscription info generated')
    return text, extra_info


def add_user_to_panel_with_old_data(user_uuid, email, traffic, expire, to_panel, to_inbound_id):
    logging.info(f'[*] Creating user {email} with old existing data')
    cookie = get_panel_session(to_panel)
    url = f'{to_panel}/panel/api/inbounds/addClient'
    headers = {'Accept': 'application/json',
               "Cookie": "; ".join([f"{k}={v}" for k, v in cookie.items()])}
    traffic = traffic
    expire = expire
    data = {
        "id": to_inbound_id,
        "settings": "{\"clients\":[{\"id\":\"" + user_uuid + "\",\"alterId\":0,\"email\":\"" + email + "\",\"limitIp\":2,\"totalGB\":" + str(traffic) + ",\"expiryTime\":" + str(int(expire)) + ",\"enable\":true,\"tgId\":\"\",\"subId\":\"\"}]}"
    }
    ses = requests.Session()
    response = ses.post(url, headers=headers, data=data)
    result = json.loads(response.content)['success']
    if response.status_code == 200 and result:
        logging.info(f"[✓] Result: User with email {email} added")
    else:
        logging.info(f"[X] Result: User with email {email} not added")


def transfer_user(username, from_panel, to_panel, flag, sub_change, from_panel_inbound_id, to_panel_inbound_id):
    from_panel = format_panel_domain(from_panel)
    to_panel = format_panel_domain(to_panel)
    logging.info(f'[*] Transfer started | User {username} from {from_panel} to {to_panel}')
    user_sub = ''

    if sub_change == 'false':
        for user in read_users():
            if user['_id'] == username:
                user_sub += user['sub']
        subscription_token = user_sub.split('/')[-1]
    else:
        subscription_token = generate_unique_token()
        user_sub = f'{sub_host_url}/sub/{subscription_token}'
    user_previous_data = get_user_old_data(panel_domain=from_panel, email=username)
    traffic = user_previous_data['traffic']
    expire = user_previous_data['expire']
    user_uuid = user_previous_data['user_uuid']
    add_user_to_panel_with_old_data(user_uuid=user_uuid, email=username, traffic=traffic, expire=expire,
                                    to_panel=to_panel, to_inbound_id=to_panel_inbound_id)

    user_to_transfer = {
        '_id': username,
        'uuid': user_uuid,
        "panel_domain": to_panel.split("//")[1].split('.')[0],
        "sub": f'{sub_host_url}/sub/{subscription_token}',
        "token": subscription_token,
        "flag": flag
    }
    logging.info(f'user_to_transfer panel domain ---> {user_to_transfer["panel_domain"]}')
    delete_client(email=username, panel_domain=from_panel,
                  inbound_id=from_panel_inbound_id)
    delete_user_from_database(username)
    users_collection.insert_one(user_to_transfer)
    save_users()
    logging.info('[✓] Transfer Complete')
    return user_sub



def extract_panel_domains():
    try:
        if not os.path.exists('users.json'):
            save_users()
        with open('users.json', 'r') as file:
            json_content = file.read()
        data = json.loads(json_content)
        panel_domains = set(format_panel_domain(entry["panel_domain"]) for entry in data)
        logging.info('[✓] panels extracted')
        return list(panel_domains)
    
    except Exception as e :
        logging.error('[X] Error extracting panels : {}'.format(e)) 

def generate_manager_configs():
    panel_domains = []
    configs_list = ""
    try:
        if not os.path.exists('users.json'):
            save_users()
        with open('users.json', 'r') as file:
            json_content = file.read()
        data = json.loads(json_content)
        
        logging.info('[✓] panels extracted')
        for entry in data:
            try:
                formatted_domain = format_panel_domain(entry["panel_domain"])
                panel_domains.append(formatted_domain)
            except Exception as e:
                continue
        panel_domains = list(set(panel_domains))    
    except Exception as e :
        logging.error(e)
    v2ray_template = "vless://{}@{}:{}?type=tcp&path=%2F&host=snap.ir&headerType=http&security=none#👑{} {}| {}"
    for panel_domain in panel_domains:
        panel_formatted =panel_domain.split('-')[0]+"."+panel_suffix
        
        flag = ''
        if 'flnd' in panel_domain:
            flag = '🇫🇮'
        elif 'nl' in panel_domain :
            flag = '🇳🇱'
        elif 'gr' in panel_domain:
            flag = '🇩🇪'
        
        configs_list+='\n'+v2ray_template.format(
            manager_uuid,
            panel_formatted.split("//")[1].split(':')[0],
            config_port,
            flag,
            panel_formatted.split("//")[1].split(':')[0].split(".")[0],
            "manager"
        )
    
    return configs_list

