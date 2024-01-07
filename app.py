from flask import Flask
#api and api endpoints
from flask_restx import Api 
from api.views import api_endpoint
from configs.config import secret_key , session_time, backup_interval , dump_interval
from flask_cors import CORS
#routes and blueprints
from routes.subscription import subscription_bp
from utils.dump import dump_panels 

# from routes.status import status_bp
import logging
from apscheduler.schedulers.background import BackgroundScheduler
logging.getLogger().setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logging.basicConfig(filename="api.log", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

app = Flask(__name__)
CORS(app)

api = Api(app)
api.add_namespace(api_endpoint)
app.register_blueprint(subscription_bp)
# app.register_blueprint(status_bp)
app.config['SECRET_KEY'] = secret_key
app.config['PERMANENT_SESSION_LIFETIME'] = session_time



if __name__ == '__main__':
    # scheduler.start()
    app.run(debug=True)
