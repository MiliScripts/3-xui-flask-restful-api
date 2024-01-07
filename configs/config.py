import yaml
from datetime import timedelta

with open('configs/config.yml', 'r') as file:
    data = yaml.safe_load(file)

#sub link endpoint
sub_host_url= data['SUB_HOST_URL']
#db
mongo_string = data['MONGO_STRING']
#panel data
panel_username = data["PANEL_USERNAME"]
panel_password = data["PANEL_PASSWORD"]
panel_port = data["PANEL_PORT"]
config_port = data["CONFIG_PORT"]
#cloudflre data
zone_id = data["ZONE_ID"]
email = data["EMAIL"]
global_api_key = data["GLOBAL_API_AKY"]
scanner_username = data["SCANNER_USERNAME"]
scanner_password = data["SCANNER_PASSWORD"]
secret_key = data['SECRET_KEY']
# status_username = data['STATUS_USERNAME']
# status_password = data['STATUS_PASSWORD']
session_time = timedelta(seconds=3600)
bot_token , bot_channel_id= data['BOT_TOKEN'],data['BOT_CHANNEL_ID']
backup_interval,dump_interval = data['BACK_UP_INTERVAL'],data['DUMP_INTERVAL']
v2ray_template = '''vless://{}@{}:{}?path=%2F&security=none&encryption=none&host={}&type=ws#{}'''
hamrah_ip_tamiz = data['hamrah']
irancell_ip_tamiz = data['irancell']
rightel_ip_tamiz = data['rightel']
wifi_ip_tamiz = data['wifi']
panel_suffix = data['panel_suffix']

emregerncy_configs ="""vmess://eyJhZGQiOiJodHRwMi1yZWwxLnBpeGVsYXRlZDQuaXIiLCJhaWQiOiIwIiwiYWxwbiI6IiIsImhvc3QiOiIiLCJpZCI6ImNhY2FhZmJmNzQ2MzQ3NDg4NDU4ZTZiY2YyZDJiZTdjIiwibmV0Ijoid3MiLCJwYXRoIjoiL3BpeGVsYXRlZCIsInBvcnQiOiI0NDMiLCJwcyI6IuKdpO+4j9in2LjYt9ix2KfYsduMINuyIiwic2N5IjoiYXV0byIsInNuaSI6Imh0dHAyLXJlbDEucGl4ZWxhdGVkNC5pciIsInRscyI6InRscyIsInR5cGUiOiIiLCJ2IjoiMiJ9

vmess://eyJhZGQiOiJodHRwMi1yZWwxLnBpeGVsYXRlZDUuaXIiLCJhaWQiOiIwIiwiYWxwbiI6IiIsImhvc3QiOiIiLCJpZCI6ImNhY2FhZmJmNzQ2MzQ3NDg4NDU4ZTZiY2YyZDJiZTdjIiwibmV0Ijoid3MiLCJwYXRoIjoiL3BpeGVsYXRlZCIsInBvcnQiOiI0NDMiLCJwcyI6IvCfkpkg2KfYuNi32LHYp9ix24wg27EiLCJzY3kiOiJhdXRvIiwic25pIjoiaHR0cDItcmVsMS5waXhlbGF0ZWQ1LmlyIiwidGxzIjoidGxzIiwidHlwZSI6IiIsInYiOiIyIn0="""
emergency_status = 0
manager_uuid = data['manager_uuid']
manager_token = data['manager_token']