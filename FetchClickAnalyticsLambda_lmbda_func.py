import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
tracking_table = dynamodb.Table('LinkTracking')

def enable_cors(status_code, body):
    """ Returns a CORS-enabled HTTP response. """
    return {
        'statusCode': status_code,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        'body': json.dumps(body)
    }

def is_valid_browser(agent):
    """ Check if the request is coming from a real web browser. """
    ua = agent.lower()
    blocked = [
        "whatsapp/", "whatsappbot", "telegrambot", "curl", "wget", "python-requests",
        "postman", "insomnia", "facebookexternalhit", "twitterbot", "linkedinbot"
    ]
    return not any(b in ua for b in blocked)

def lambda_handler(event, context):
    try:
        if event.get("httpMethod") == "OPTIONS":
            return enable_cors(200, "CORS preflight OK")

        query_params = event.get('queryStringParameters', {})
        if not query_params or 'trackId' not in query_params:
            return enable_cors(400, {'error': 'trackId is required'})

        track_id = query_params['trackId']

        headers = event.get('headers', {})
        print(f"Received Headers: {headers}")

        user_agent = headers.get('User-Agent') or headers.get('user-agent', '')
        print(f"Extracted User-Agent: {user_agent}")

        if not is_valid_browser(user_agent):
            print(f"Blocked: {user_agent}")
            return enable_cors(400, {'error': 'Blocked non-browser agent'})

        response = tracking_table.query(
            KeyConditionExpression=Key("trackId").eq(track_id)
        )
        clicks = response.get('Items', [])
        total = len(clicks)

        print(f"Query Result: {response}")

        return enable_cors(200, {
            "trackId": track_id,
            "totalClicks": total,
            "clickDetails": clicks
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return enable_cors(500, {'error': f'Internal Error: {str(e)}'})
