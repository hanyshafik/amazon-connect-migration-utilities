import boto3
import os
import sys
import json
import pydash as _

mapping = {}

with open(os.path.join(sys.path[0], 'source-manifest-config.json'), "r") as file:
    config = json.load(file)

client = boto3.client('connect')


def get_types():
    paginator = client.get_paginator('list_contact_flow_modules')
    mapping["ContactFlowModulesSummaryList"] = {}
    for page in paginator.paginate(InstanceId=config["ConnectInstanceId"],
                                   ContactFlowModuleState="active",
                                   PaginationConfig={
                                                     "MaxItems": 50,
                                                     "PageSize": 50,
                                    }):
        for module in page["ContactFlowModulesSummaryList"]:
            mapping["ContactFlowModulesSummaryList"][module["Name"]] = {
                "Arn": module["Arn"],
                "Id": module["Id"]
            }

    paginator = client.get_paginator('list_contact_flows')
    for page in paginator.paginate(InstanceId=config["ConnectInstanceId"],
                                   ContactFlowTypes=['CONTACT_FLOW',
                                                     'CUSTOMER_QUEUE',
                                                     'CUSTOMER_HOLD',
                                                     'CUSTOMER_WHISPER',
                                                     'AGENT_HOLD',
                                                     'AGENT_WHISPER',
                                                     'OUTBOUND_WHISPER',
                                                     'AGENT_TRANSFER',
                                                     'QUEUE_TRANSFER'],
                                   PaginationConfig={
                                                     "MaxItems": 50,
                                                     "PageSize": 50,
                                    }):
        mapping["ContactFlowSummaryList"] = {}
        for module in page["ContactFlowSummaryList"]:
            print(module)
            mapping["ContactFlowSummaryList"][module["Name"]] = {
                "Arn": module["Arn"],
                "Id": module["Id"]
            }

    paginator = client.get_paginator('list_hours_of_operations')
    for page in paginator.paginate(InstanceId=config["ConnectInstanceId"],
                                   PaginationConfig={
                                                     "MaxItems": 50,
                                                     "PageSize": 50,
                                    }):
        mapping["HoursOfOperationSummaryList"] = {}
        for module in page["HoursOfOperationSummaryList"]:
            mapping["HoursOfOperationSummaryList"][module["Name"]] = module["Arn"]

    paginator = client.get_paginator('list_phone_numbers')
    for page in paginator.paginate(InstanceId=config["ConnectInstanceId"],
                                   PhoneNumberTypes=["TOLL_FREE", "DID"],
                                   PaginationConfig={
                                                     "MaxItems": 50,
                                                     "PageSize": 50,
                                    }):
        mapping["PhoneNumberSummaryList"] = {}
        for module in page["PhoneNumberSummaryList"]:
            mapping["PhoneNumberSummaryList"][module["PhoneNumber"]] = {
                "Arn": module["Arn"],
                "Name": module["PhoneNumber"]
            }

    paginator = client.get_paginator('list_prompts')
    for page in paginator.paginate(InstanceId=config["ConnectInstanceId"],
                                   PaginationConfig={
                                                     "MaxItems": 50,
                                                     "PageSize": 50,
                                    }):
        mapping["PromptSummaryList"] = {}
        for module in page["PromptSummaryList"]:
            mapping["PromptSummaryList"][module["Name"]] = {
                "Arn": module["Arn"],
                "Id": module["Id"]
            }

    paginator = client.get_paginator('list_queues')
    for page in paginator.paginate(InstanceId=config["ConnectInstanceId"],
                                   QueueTypes=["STANDARD", "AGENT"],
                                   PaginationConfig={
                                                     "MaxItems": 50,
                                                     "PageSize": 50,
                                    }):
        mapping["QueueSummaryList"] = {}
        for module in page["QueueSummaryList"]:
            if "Name" not in module:
                continue
            mapping["QueueSummaryList"][module["Name"]] = {
                "Arn": module["Arn"],
                "Id": _.get(module, "Id")
            }
    paginator = client.get_paginator('list_quick_connects')
    for page in paginator.paginate(InstanceId=config["ConnectInstanceId"],
                                   QuickConnectTypes=["USER", "QUEUE", "PHONE_NUMBER"],
                                   PaginationConfig={
                                                     "MaxItems": 50,
                                                     "PageSize": 50,
                                    }):
        mapping["QuickConnectSummaryList"] = {}
        for module in page["QuickConnectSummaryList"]:
            mapping["QuickConnectSummaryList"][module["Name"]] = {
                "Arn": module["Arn"],
                "Id": module["Id"]
            }

    paginator = client.get_paginator('list_routing_profiles')
    for page in paginator.paginate(InstanceId=config["ConnectInstanceId"],
                                   PaginationConfig={
                                                     "MaxItems": 50,
                                                     "PageSize": 50,
                                    }):
        mapping["RoutingProfileSummaryList"] = {}
        for module in page["RoutingProfileSummaryList"]:
            mapping["RoutingProfileSummaryList"][module["Name"]] = {
                "Arn": module["Arn"],
                "Id": module["Id"]
            }

    lexv2_client = boto3.client('lexv2-models')
    response = lexv2_client.list_bots()
    bot_definitions = {}
    while(True):
        for bot_definition in response["botSummaries"]:
            bot_definitions[bot_definition["botName"]] = {
                "botId": bot_definition["botId"],
                "botName": bot_definition["botName"],
                "botAliases": []
            }
        if "nextToken" not in response:
            break
        response = lexv2_client.list_bots(nextToken=response["nextToken"])

    for bot_name in bot_definitions:
        response = lexv2_client.list_bot_aliases(botId=bot_definitions[bot_name]["botId"])
        while(True):
            for bot_alias in response["botAliasSummaries"]:
                bot_definitions[bot_name]["botAliases"].append({
                    "botAliasId": bot_alias["botAliasId"],
                    "botAliasName": bot_alias["botAliasName"]
                })
            if "nextToken" not in response:
                break
            response = lexv2_client.list_bot_aliases(botId=bot_definitions[bot_name]["botId"])

    mapping["LexBotSummaries"] = bot_definitions


get_types()
with open(os.path.join(sys.path[0], config["ManifestFileName"]), 'w') as f:
    json.dump(mapping, f, indent=4, default=str)
