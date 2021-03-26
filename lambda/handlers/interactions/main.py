import os
import awsgi
import boto3
from commands.server import route_server_command
from discord_interactions import verify_key_decorator
from flask import (
    Flask,
    jsonify,
    request,
)

PUBLIC_KEY = os.environ.get('APPLICATION_ID')

app = Flask(__name__)

@app.route('/discord', methods=['POST'])
@verify_key_decorator(PUBLIC_KEY)
def index():

    print(request.json)
    if request.json["type"] == 1:
        return jsonify({"type": 1})
    else:

        command =  request.json["data"]["options"][0]['name']

        response = route_command(command, request)

        print(response)

        return jsonify({
            "type": 4,
            "data": {
                "content": response
            }
        })

def route_command(command, request):

    commands = {
        'server': route_server_command
    }

    return commands[command](request)

def lambda_handler(event, context):
    
    print(event)

    return awsgi.response(
        app,
        event,
        context,
        base64_content_types={"image/png"}
    )