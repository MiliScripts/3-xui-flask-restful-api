from flask_restx import Resource, Namespace, abort 
from flask import jsonify, request
from utils.tools import *
from utils.xui_utils import *
from utils.db_tools import  read_users
from controler import *
from utils.panels_status import get_panels
from utils.get_services import get_users_services 



api_endpoint = Namespace('api')
#_______________json responses____________________
def success_response(data, message=""):
    return jsonify({"status": "success", "data": data, "message": message})

def error_response(message):
    return jsonify({"status": "error", "message": message})


#________________get list of all users____________________
@api_endpoint.route('/users')
class GetAllUsers(Resource):
    def get(self):
        return success_response(data={'result': read_users()})


#________________get info of a user____________________
@api_endpoint.route('/user/get/<string:username>')
class GetUser(Resource):
    def get(self, username):
        return success_response({'user': get_user_from_database(username)})


#________________delete user from db____________________
@api_endpoint.route('/user/delete/<string:username>')
class DeleteUser(Resource):
    def delete(self, username):
        print('[*] deleting user {} from db and panel '.format(username))

        user = get_user_from_database(username)
        print(user)
        if not user:
            abort(404, message=f"User '{username}' not found")
        #remove client from panel
        user_panel_domain=format_panel_domain(user['panel_domain'])
        print(user_panel_domain)
        try:
            delete_client(email=user['_id'],
                        panel_domain=user_panel_domain
                        ,inbound_id=1)
            
            result = delete_user_from_database(username) 
            return jsonify({'result':result})
        except Exception as e  :
            return jsonify({"result": e})


#________________create user in the panel____________________
@api_endpoint.route('/user/create')
class CreateVlessUser(Resource):
    def post(self):
        args = request.json
      
        return jsonify({
                'subscription_link': add_user(
                    username=args['username'],
                    panel_domain=args['panel_domain'],
                    inbound_id=args['inbound_id'],
                    flag=args['flag'],
                    traffic=args['traffic'],
                    expire_days=args['expire_days']
                ), 'result': 'created'
            })
        


#_______________update a user in terms of sublink and also in the panel____________________
@api_endpoint.route('/user/update')
class UpdateUser(Resource):
    def put(self):
        print(request.json)

        # List of possible posted arguments
        args = request.json
        username = args.get('username')
        panel_domain = args.get('panel_domain', None)
        traffic = args.get('traffic', None)
        expire_days = args.get('expire_days', None)
        inbound_id = args.get('inbound_id', None)
        sub_change = args.get('sub_change', 'false')
        flag = args.get('flag',get_user_from_database(username)['flag'])

        if username and panel_domain:
            try:
                return jsonify({
                    'process result': update_user(
                        username=username,
                        panel_domain=panel_domain,
                        sub_change=sub_change,
                        flag=args.get('flag'),
                        inbound_id=inbound_id,
                        traffic=traffic,
                        expire_days=expire_days,
                    ), 'result': 'update succeed'
                })
            except Exception as e:
                return jsonify({'error': str(e)})
        else:
            return jsonify({'error': "username or panel domain not provided"})


#________________transfer user from one panel to another____________________
@api_endpoint.route('/user/transfer')
class TransferUser(Resource):
    def post(self):
        args = request.json
        try:
            return jsonify({
                'subscription_link': transfer_user(
                    username=args['username'],
                    from_panel=args['from_panel'],
                    to_panel=args['to_panel'],
                    flag=args['flag'],
                    sub_change=args['sub_change'],
                    to_panel_inbound_id=args['to_panel_inbound_id'],
                    from_panel_inbound_id=args['from_panel_inbound_id'],
                ),
                'result': 'user transferred from {} to {}'.format(args['from_panel'], args['to_panel'])
            })
        except Exception as e:
            return str(e)



#________________get panel's status____________________
@api_endpoint.route('/get/panels')
class GetPanelsStatus(Resource):
    def get(self):
        try:
            data = get_panels()
            return jsonify({'result':data})
        except Exception as e:
            return jsonify({"result":'getting panels status failed [{}]'.format(e)})
        
    
#________________get user's services
@api_endpoint.route('/get/user/services/<string:userid>')
class GetUserServices(Resource):
    def get(self,userid):
        print(userid)
        try:
            return jsonify({"result":get_users_services(user_id=userid)})
        except:
            return jsonify({"reult":'fsiled to get user {} services'.format(userid)})
    
    
    
#__________________get sub detail ___________
@api_endpoint.route('/get/sub')
class GetUserSubDetail(Resource):
    def post(self):
        args = request.json
        sub_token = args['sub_url'].split('/')[-1]
        
        for user in read_users():
            if user['token'] == sub_token:
                return jsonify({'result':user})
 
        else:
            return jsonify({"result" : 'cant fetch user data (not existed in db)'})
    
    
    