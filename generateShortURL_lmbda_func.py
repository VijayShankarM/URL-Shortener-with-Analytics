import json
import boto3
import hashlib
import time

# Change to your actual DynamoDB table name
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('URLShortenerTable')  # ✅ Renamed from 'ShortenedURLs' to 'URLShortenerTable'

# Replace with your actual API Gateway or CloudFront URL
BASE_URL = "https://your-api-id.execute-api.region.amazonaws.com/prod"  # ✅ Update this to your actual base URL

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
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            'body': json.dumps({
                'shortCode': short_code,
                'shortURL': f"{BASE_URL}/{short_code}"
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
