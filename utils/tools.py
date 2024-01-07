import base64
import secrets
import datetime
import jdatetime
import random
from configs.config import *
import string
import re
import requests
def generate_unique_token():
    # Generate a URL-safe random token
    token = secrets.token_urlsafe(32)
    return token

# Encode a text to base64
def encode_to_base64(text):
    encoded_bytes = base64.b64encode(text.encode('utf-8'))
    encoded_text = encoded_bytes.decode('utf-8')
    return encoded_text

# Decode a text from base64
def decode_from_base64(encoded_text):
    decoded_bytes = base64.b64decode(encoded_text.encode('utf-8'))
    decoded_text = decoded_bytes.decode('utf-8')
    return decoded_text


iranian_months = {
    "farvardin": "فروردین",
    "ordibehesht": "اردیبهشت",
    "khordad": "خرداد",
    "tir": "تیر",
    "mordad": "مرداد",
    "shahrivar": "شهریور",
    "mehr": "مهر",
    "aban": "آبان",
    "azar": "آذر",
    "dey": "دی",
    "bahman": "بهمن",
    "esfand": "اسفند"
}

# Function to calculate the difference in days between a given timestamp and the current date
def date_difference_in_days(timestamp):
    today = datetime.datetime.now()
    td = datetime.datetime.fromtimestamp(timestamp // 1000)
    difference = td - today
    return difference.days


# Function to convert bytes to gigabytes or megabytes based on the size
def bytes_to_gb_mb(bytes):
    if bytes >= 1073741824:  # 1 gigabyte in bytes
        return f"{round(bytes / 1073741824,2)} GB"
    else:
        return f"{round(bytes / 1048576,2)} MB"

# Function to convert a timestamp to Jalali date format
def timestamp_to_jalali(timestamp_ms):
    timestamp_sec = timestamp_ms / 1000  # convert milliseconds to seconds
    jalali_date = jdatetime.datetime.fromtimestamp(timestamp_sec).strftime('%d %B')
    return jalali_date


def meow_jalali(timestamp_ms):
    timestamp_sec = timestamp_ms / 1000  # convert milliseconds to seconds
    
    true_time = str(datetime.datetime.fromtimestamp(timestamp_sec)).split(' ')[-1].split('.')[0]
    
    jalali_date = str(jdatetime.datetime.fromtimestamp(timestamp_sec).strftime('%Y/%m/%d')) + '| {}'.format(true_time)
    
    return jalali_date


def format_traffic(bytes):
    if bytes < 1024:
        return f"{bytes:.2f} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes / (1024 * 1024 * 1024):.2f} GB"




def days_to_timestamp(days):
    if days==0:
        return 0
    now = datetime.datetime.now()
    future_date = now + datetime.timedelta(days=days)
    timestamp = future_date.timestamp()

    return timestamp

def gb_to_bytes(gb):
    if gb==0:
        return 0
    bytes = gb * 1024 * 1024 * 1024
    return bytes



def format_panel_domain(panel_domain):
    return f'http://{panel_domain}.{panel_suffix}:{panel_port}'



def make_user_config(user_uuid,username,user_panel):
    template = "vless://{}@{}.{}:{}?type=tcp&path=%2F&host=snap.ir&headerType=http&security=none#{}".format(
        user_uuid,
        user_panel.split('-')[0],
        panel_suffix,
        config_port,
        username
    )
    return template