# URL Shortener with Click Analytics

## Project Overview
This project is a **serverless URL shortener** that allows users to shorten long URLs and track analytics for each shortened URL. It also provides insights into user interactions, such as the number of clicks, timestamps, IP addresses, and User-Agent details.

## Features
- Shorten long URLs into unique short codes
- Redirect users to the original URL when accessing a short link
- Track click analytics, including:
  - Timestamp of each visit
  - IP address of the visitor
  - User-Agent to determine the type of device/browser
- Filter analytics to show only web browser-based clicks
- Support for CORS to allow frontend integration
- Serverless architecture using AWS services

## Tech Stack
- **Frontend**: HTML, JavaScript (for user interaction)
- **Backend**: AWS Lambda, API Gateway, DynamoDB
- **Storage**: DynamoDB for storing URLs and analytics data
- **Security**: CORS enabled for API access

## Step-by-Step Implementation

### 1. Setting Up AWS Services
- Create an **S3 bucket** to host the frontend (optional if using a web interface).
- Create a **DynamoDB table** to store the shortened URLs.
- Create another **DynamoDB table** to store click analytics.
- Create an **API Gateway** to handle URL shortening and redirection.
- Create **AWS Lambda functions** for:
  - Generating a short URL
  - Redirecting users to the original URL
  - Tracking analytics for each visit
  - Retrieving analytics data for reporting

### 2. Implementing URL Shortening
- Accept long URLs as input.
- Generate a unique short code for each URL.
- Store the mapping in DynamoDB.
- Return the short URL to the user.

### 3. Handling Redirection and Tracking Clicks
- Capture incoming requests for short links.
- Look up the corresponding long URL in DynamoDB.
- Record analytics data including IP, timestamp, and User-Agent.
- Filter out non-browser User-Agents (e.g., WhatsApp, bots, etc.).
- Redirect users to the original URL.

### 4. Fetching Click Analytics
- Retrieve all recorded visits for a specific short URL.
- Count only browser-based clicks.
- Return analytics data in a structured format.

## Future Enhancements
- Add user authentication to manage URL history.
- Implement expiration dates for short links.
- Enhance analytics with geographical location tracking.
- Build a more interactive frontend for analytics visualization.

## Conclusion
This **serverless URL shortener with analytics** provides an efficient way to manage and track shortened URLs. By leveraging AWS services, the project ensures scalability, low-cost operation, and real-time analytics for user interactions.

