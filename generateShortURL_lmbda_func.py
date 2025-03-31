import json
import boto3
import hashlib
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ShortenedURLs')

# Replace this with your actual domain (CloudFront or API Gateway)
BASE_URL = "https://pilvnjuvog.execute-api.us-east-1.amazonaws.com/prod"

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        long_url = body['longURL']
        
        # Generate a short hash code
        short_code = hashlib.md5(long_url.encode()).hexdigest()[:6]
        
        # Store in DynamoDB
        table.put_item(
            Item={
                'shortCode': short_code,
                'longURL': long_url,
                'clicks': 0,
                'createdAt': str(time.time())
            }
        )
        
        # Success response with CORS headers
        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # Allow all origins
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            'body': json.dumps({
                'shortCode': short_code,
                'shortURL': f"{BASE_URL}/{short_code}"  # Use actual API Gateway URL
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            'body': json.dumps({"error": str(e)})
        }
