def get_named_parameter(event, name):
    return next(item for item in event['parameters'] if item['name'] == name)['value']


def get_named_property(event, name):
    return next(
        item for item in
        event['requestBody']['content']['application/json']['properties']
        if item['name'] == name)['value']


def lambda_handler(event, context):
    # Getting information from event
    action_group = event['actionGroup']
    api_path = event['apiPath']
    http_method = event['httpMethod']

    # getting parameters according to the http method
    if http_method == "get":
        claim_id = get_named_parameter(event, "claim_id")
    elif http_method == "post":
        claim_id = get_named_property(event, "claim_id")

    # setting expected response body
    response_body = {
        'application/json': {
            'body': "sample response"
        }
    }

    # Logic to process the request goes here
    ...

    # Lastly, return the response to the agent
    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }

    api_response = {
        'messageVersion': '1.0',
        'response': action_response
    }

    return api_response
