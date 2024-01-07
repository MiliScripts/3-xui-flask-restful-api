
import json
import requests
from utils.db_tools import save_users
from utils.xui_utils import get_panel_session
from utils.tools import format_panel_domain
from utils.dump import dump_panels
import os


if not os.path.exists('panels_dump'):
    os.makedirs('panels_dump')
    
if len(os.listdir('panels_dump'))==0:
        dump_panels()
    

def extract_panel_domains():
    if not os.path.exists('users.json'):
        save_users()
    with open('users.json', 'r') as file:
        json_content = file.read()
    data = json.loads(json_content)
    panel_domains = set(entry["panel_domain"] for entry in data)
    return list(panel_domains)


def get_online_user(panel_domain)->int:
    cookie = get_panel_session(panel_domain)
    panel_domain = format_panel_domain(panel_domain)
    try:
        header = {
            "Accept": "application/json",
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookie.items()])
        }
        url = f"{panel_domain}/panel/api/inbounds/onlines"
        ses = requests.Session()
        response = ses.post(url, headers=header)
        data = json.loads(response.content)['obj']
        return len(data)
    except Exception as e :
       print(e)
       
       


def get_panel_users_type(panel_domain):
    panel_name = panel_domain.split('/')[-1].split(':')[0].split('.')[0]
    active = 0
    expired = 0
    with open('panels_dump/{}.json'.format(panel_name),'r') as f :
        data = json.load(f)
    for i in data :
        if data[i]['status']==True:
            active+=1
        else:
            expired+=1
    all_users = active+expired
    users_status = {'all':all_users,'active':active,'expired':expired}
    
    return users_status

def get_panels():
    list_od_panel_status = {}
    for i in extract_panel_domains():
        list_od_panel_status[i] = get_panel_users_type(i)
        
    
    return list_od_panel_status


