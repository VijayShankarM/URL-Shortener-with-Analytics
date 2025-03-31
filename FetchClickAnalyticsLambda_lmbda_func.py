import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
analytics_table = dynamodb.Table('ClickAnalytics')

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

def is_browser(user_agent):
    """ Check if the request is coming from a real web browser. """
    # Convert to lowercase for consistency
    ua = user_agent.lower()

    # List of non-browser user-agents to block
    blocked_agents = [
        "whatsapp/", "whatsappbot", "telegrambot", "curl", "wget", "python-requests",
        "postman", "insomnia", "facebookexternalhit", "twitterbot", "linkedinbot"
    ]

    # Block any User-Agent that matches our list
    return not any(agent in ua for agent in blocked_agents)

def lambda_handler(event, context):
    try:
        # Handle CORS Preflight Request
        if event.get("httpMethod") == "OPTIONS":
            return cors_response(200, "Preflight CORS response")

        # Extract shortCode from query parameters
        query_params = event.get('queryStringParameters', {})
        if not query_params or 'shortCode' not in query_params:
            return cors_response(400, {'error': 'Short code is required'})

        short_code = query_params['shortCode']

        # Extract all headers (log them for debugging)
        headers = event.get('headers', {})
        print(f"Received Headers: {headers}")

        # Normalize header keys to lowercase (API Gateway may change them)
        user_agent = headers.get('User-Agent') or headers.get('user-agent', '')

        # Debugging: Log the exact User-Agent
        print(f"Extracted User-Agent: {user_agent}")

        # Block requests from non-browser sources
        if not is_browser(user_agent):
            print(f"Blocked non-browser request: {user_agent}")
            return cors_response(400, {'error': 'Non-browser request detected'})

        # Query DynamoDB for analytics data
        response = analytics_table.query(
            KeyConditionExpression=Key("shortCode").eq(short_code)
        )
        click_details = response.get('Items', [])
        total_clicks = len(click_details)

        # Debugging: Log the response for verification
        print(f"Query Result: {response}")

        return cors_response(200, {
            "shortCode": short_code,
            "totalClicks": total_clicks,
            "clickDetails": click_details
        })

    except Exception as e:
        print(f"Error fetching analytics: {str(e)}")
        return cors_response(500, {'error': f'Failed to fetch analytics: {str(e)}'})
