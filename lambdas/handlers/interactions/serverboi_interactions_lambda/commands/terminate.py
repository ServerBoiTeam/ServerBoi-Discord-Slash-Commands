from flask import request
from botocore.exceptions import ClientError as BotoClientError
import boto3
import os
import json
import serverboi_utils.responses as response_utils
import serverboi_utils.embeds as embed_utils
from uuid import uuid4
from discord import Color


TERMINATE_ARN = os.environ.get("PROVISION_ARN")


def route_terminate_command(request: request) -> dict:
    server_command = request.json["data"]["options"][0]["options"][0]["name"]

    server_commands = {"valheim": terminate_server}

    # Set user info
    create_server_kwargs = {}
    create_server_kwargs["game"] = server_command
    create_server_kwargs["user_id"] = request.json["member"]["user"]["id"]
    create_server_kwargs["username"] = request.json["member"]["user"]["username"]

    # Set interaction info
    create_server_kwargs["interaction_id"] = request.json["id"]
    create_server_kwargs["interaction_token"] = request.json["token"]
    create_server_kwargs["application_id"] = request.json["application_id"]

    options = request.json["data"]["options"][0]["options"][0]["options"]

    for option in options:
        create_server_kwargs[option["name"]] = option["value"]

    return server_commands[server_command](**create_server_kwargs)


def terminate_server(**kwargs) -> str:
    sfn = boto3.client("stepfunctions")

    execution_name = uuid4().hex.upper()

    kwargs["execution_name"] = execution_name
    data = json.dumps(kwargs)

    sfn.start_execution(stateMachineArn=TERMINATE_ARN, name=execution_name, input=data)

    parameter_data = kwargs

    key_to_remove = [
        "interaction_id",
        "interaction_token",
        "application_id",
        "username",
        "user_id",
        "game",
        "execution_name",
    ]
    for key in key_to_remove:
        parameter_data.pop(key)

    embed = embed_utils.form_workflow_embed(
        workflow_name=f"Provision-Server",
        workflow_description=f"Workflow ID: {execution_name}",
        status="⏳ Pending",
        stage="Starting...",
        color=Color.greyple(),
    )

    data = response_utils.form_response_data(embeds=[embed])

    return data