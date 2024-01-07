import json
import requests 
from datetime import datetime
from configs.config import panel_username , panel_password
from utils.xui_utils import get_client_data
import os
from utils.tools import format_panel_domain
import logging
from utils.db_tools import save_users
save_users()
with open('users.json','r') as f :
    users = json.load(f)
    
    
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
    logging.info('[*] dumping {} paneldata to file '.format(panel_domain))
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
        with open('panels_dump/'+panel_domain.split('/')[-1].split(':')[0].split('.')[0]+'.json','w') as f:
            json.dump(data_to_save,f) 
            logging.info('[✓] dumping {} data to file done'.format(panel_domain))     
            return
    except Exception as e :
        logging.error("[X] cant dump {} panel data | Error : {}".format(panel_domain,e))         

def dump_panels():      
    
    dumped_panels = []    
    failed_panels = []    
    for panel in extract_panel_domains():
        try:
            dump_panel(panel_domain=panel)
            dumped_panels+=panel.split('/')[-1].split(':')[0].split('.')[0]
        except Exception as e :
            failed_panels+=panel.split('/')[-1].split(':')[0].split('.')[0]
            logging.info('[X] skipping dumping {} data | Error : {}'.format(panel,e))
            continue
    
    logging.info('[✓] all panels dumped')
    logging.info('[✓] dumped : {}'.format(','.join(dumped_panels)))
    logging.info('[X] failed dump panels : {}'.format(','.join(failed_panels)))
        
            
        
        



