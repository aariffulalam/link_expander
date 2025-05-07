# Link Expander API

This is a FastAPI-based project for expanding shortened URLs and logging the results into a database.

---

## Features
- Expand shortened URLs using custom logic and external scrapers.
- Log URL expansion results into a MySQL database.
- Handle specific URL patterns like Flipkart links.
- Send email notifications using AWS SNS.

---

## Prerequisites
Before running the project, ensure you have the following installed:
- Python 3.9 or higher
- Docker (optional, for containerized deployment)
- AWS account with SNS and SES configured

---

## Installation

### 1. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up the `.env` File
Create a `.env` file in the root directory with the following content:
```properties
# AWS Configuration
AWS_DEFAULT_REGION=your-region
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key

# SNS Topic ARN
SNS_EMAIL_ARN=arn:aws:sns:your-region:123456789012:YourTopicName

# Email Configuration
EMAIL_FROM_EMAIL=your-sender-email@example.com
EMAIL_FROM_NAME=Your Sender Name
```

---

## Setting Up AWS SNS for Email Notifications

### 1. Create an SNS Topic
1. Go to the **AWS SNS Console**.
2. Create a new SNS topic (or use an existing one).
3. Note the **Topic ARN** (e.g., `arn:aws:sns:us-east-1:123456789012:YourTopicName`).

### 2. Subscribe Recipients to the SNS Topic
1. In the SNS Console, select the topic you created.
2. Add subscriptions for the email addresses:
   - Click **Create subscription**.
   - Set **Protocol** to `Email`.
   - Enter the email address (e.g., `aarif@jetbro.in`).
   - Repeat for `dilip@lehlah.in`.
3. Confirm the subscription:
   - AWS will send a confirmation email to each recipient.
   - The recipients must click the confirmation link in the email to activate the subscription.

### 3. Update the `.env` File
Set the `SNS_EMAIL_ARN` environment variable in the `.env` file to the ARN of your SNS topic:
```properties
SNS_EMAIL_ARN=arn:aws:sns:your-region:123456789012:YourTopicName
```

---

## Running the Application

### 1. Start the Server
Run the FastAPI server:
```bash
uvicorn app.main:app --reload
```

### 2. Access the API
The API will be available at:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Sending Emails
The application uses AWS SNS to send email notifications. When a URL expansion fails, an email is sent to all subscribers of the SNS topic specified in the `SNS_EMAIL_ARN` environment variable.

### Example Email Notification
- **Subject**: URL Expansion Failed Notification
- **Body**:
  ```
  URL: https://example.com
  Expanded_URL: https://expanded-example.com
  Error: Invalid URL format
  ```

---

## Testing the Email Functionality

### 1. Trigger an Email
Make a POST request to the `/expand` endpoint with an invalid URL to trigger an email notification:
```bash
curl -X POST http://127.0.0.1:8000/expand \
-H "Content-Type: application/json" \
-d '{"url": "https://invalid-url"}'
```

### 2. Check the Recipients' Inboxes
Ensure that the recipients (`aarif@jetbro.in` and `dilip@lehlah.in`) receive the email notification.

---

## Common Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Server
```bash
uvicorn app.main:app --reload
```

### Test the API
```bash
curl -X POST http://127.0.0.1:8000/expand \
-H "Content-Type: application/json" \
-d '{"url": "https://fkrt.it/example"}'
```

---
