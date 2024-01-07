from flask import Blueprint , request , render_template
from utils.db_tools import read_users , get_user_from_database
from utils.tools import encode_to_base64 , format_traffic , format_panel_domain , make_user_config
from controler import generate_subscription_status_config , generate_manager_configs
from configs.config import *
subscription_bp = Blueprint('subscription', __name__)






@subscription_bp.route('/sub/<string:sub_token>')
def handle_user_sub_link(sub_token):
    #check if manager 
    if sub_token==manager_token:
        return generate_manager_configs()
    try:
        for user in read_users():
            if user['token'] == sub_token:
                print('yes-----------')
                
                
                
            
                user_email = user['_id']
                subscriber = get_user_from_database(user['_id'])
                panel_domain = subscriber["panel_domain"]
                user_config_uuid = subscriber['uuid']
                user_config_name = user['_id']
                if '-' in user['_id'] :
                    user_config_name = user['_id'].split('-')[1]
                
                configs = make_user_config(user_uuid=user_config_uuid,
                                           username=user_config_name,
                                           user_panel=panel_domain)
                
                status_config = generate_subscription_status_config(
                    username=user_email,
                    panel_domain=format_panel_domain(panel_domain),
                )
                text = status_config[0].format(configs)

                encoded_text = text
                user_agent = request.headers.get('User-Agent')
                user_agents = ["Mozila", "Chrome", "Safari", "Opera", "Edge", "Firefox"]
                
                for i in user_agents:
                    if i in user_agent:
                        data = status_config[1]
                        username = data['user_name']
                        status = data['status']
                        total_byte = data['total_byte']
                        usage_byte = data['usage_byte']
                        display_value = 'نامحدود'

                        remaining_byte = total_byte - usage_byte
                        remaining_traffic = format_traffic(remaining_byte)
                        expire_date = data['expire_date']

                        remaining = data['remainig_days']

                        if data['total_byte'] == 0:
                            display_value == 'نامحدود'
                        else:
                            display_value = format_traffic(data['total_byte'])
                            

                        if display_value == 'نامحدود':
                            return render_template('subscription.html', username=username, status=status + ' نامحدود',
                                                sub=request.url)
                        else:
                            return render_template('subscription.html', username=username, status=status, sub=request.url, rh=True,
                                                remaining_traffic=remaining_traffic, display_value=display_value,
                                                expire_date=expire_date, remaining=remaining)

                else:
                    if emergency_status==1:
                        
                        return encoded_text+emregerncy_configs
                    else:
                        return encoded_text
        else:        
            print('user with token [ {} ] not found !'.format(sub_token))  
            return render_template('404.html')        
    except Exception as e :
       print(e)
       return render_template('404.html')