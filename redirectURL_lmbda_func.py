import json
import boto3
from datetime import datetime, timedelta

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
url_table = dynamodb.Table('URLShortenerTable')
clicks_table = dynamodb.Table('URLClickAnalyticsTable')

def is_browser(user_agent):
    """ Check if the request is coming from a real web browser. """
    ua = user_agent.lower()

    # Block non-browser user-agents
    blocked_agents = [
        "whatsapp/", "whatsappbot", "telegrambot", "curl", "wget", "python-requests",
        "postman", "insomnia", "facebookexternalhit", "twitterbot", "linkedinbot"
    ]

    return not any(agent in ua for agent in blocked_agents)

def lambda_handler(event, context):
    try:
        # Handle CORS Preflight Request
        if event.get("httpMethod") == "OPTIONS":
            return cors_response(200, "Preflight CORS response")

        path_params = event.get('pathParameters', {})
        short_code = path_params.get('shortCode')

        if not short_code:
            return cors_response(400, {'error': 'Short code is required'})

        # Fetch URL details
        response = url_table.get_item(Key={'shortCode': short_code})
        if 'Item' not in response:
            return cors_response(404, {'error': 'URL not found'})

        long_url = response['Item']['longURL']

        # Extract IP and User-Agent
        ip_address = get_ip_address(event)
        user_agent = event.get('headers', {}).get('User-Agent', 'Unknown')

        print(f"Extracted User-Agent: {user_agent}")

        # Block if request is not from a real browser
        if not is_browser(user_agent):
            print(f"Blocked non-browser request: {user_agent}")
            return cors_response(400, {'error': 'Non-browser request detected'})

        # Convert to IST timestamp
        timestamp_ist = get_ist_timestamp()

        # Log only real browser clicks
        clicks_table.put_item(
            Item={
                'shortCode': short_code,
                'timestamp': timestamp_ist,
                'ipAddress': ip_address,
                'userAgent': user_agent
            }
        )

        # Redirect to Long URL
        return {
            'statusCode': 302,
            'headers': {
                "Location": long_url,
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            'body': json.dumps({'message': 'Redirecting to the long URL'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return cors_response(500, {'error': str(e)})

def get_ip_address(event):
    """ Extracts user's IP address from event. """
    request_context = event.get('requestContext', {}) or {}
    identity = request_context.get('identity', {}) or {}
    return identity.get('sourceIp') or event.get('headers', {}).get('X-Forwarded-For', 'Unknown')

def get_ist_timestamp():
    """ Converts UTC to IST time format. """
    utc_time = datetime.utcnow()
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime("%Y-%m-%d %H:%M:%S")

def cors_response(status_code, body):
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
