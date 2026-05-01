# 🚀 HR Claim Handler – AWS Lambda Function (ALPHA version)

This Lambda function handles HR-related claim requests. It supports both `GET` and `POST` methods and extracts the `claim_id` from the request.

---

## 📁 Project Structure

```
my-lambda/
├── lambda_function.py
├── README.md
├── trust-policy.json   # only if creating a new role
└── function.zip         # generated during packaging
```

---

## 🛠️ Step-by-Step Deployment with AWS CLI

### 1️⃣ Zip the Lambda Function

```bash
zip function.zip lambda_function.py
```

---

### 2️⃣ Create an IAM Role (if not already created)

#### 👉 Create a trust policy file

Save the following as `trust-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

#### 👉 Create the IAM role

```bash
aws iam create-role \
  --role-name lambda-basic-execution \
  --assume-role-policy-document file://trust-policy.json
```

#### 👉 Attach permissions to the role

```bash
aws iam attach-role-policy \
  --role-name lambda-basic-execution \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

⏳ *Wait 10–20 seconds before proceeding to allow IAM changes to propagate.*

---

### 3️⃣ Create the Lambda Function

```bash
aws lambda create-function \
  --function-name hr-claim-handler \
  --runtime python3.11 \
  --role arn:aws:iam::<your-account-id>:role/lambda-basic-execution \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip
```

> 🔁 Replace `<your-account-id>` with your actual AWS Account ID.

---

### 4️⃣ Test the Lambda (Optional)

#### 👉 Create a test event `event.json`

```json
{
  "actionGroup": "hr-claims",
  "apiPath": "/get-claim",
  "httpMethod": "get",
  "parameters": [
    {
      "name": "claim_id",
      "value": "ABC123"
    }
  ]
}
```

#### 👉 Invoke the Lambda

```bash
aws lambda invoke \
  --function-name hr-claim-handler \
  --payload fileb://event.json \
  output.json

cat output.json
```

---

### 5️⃣ Update Lambda Function Code (If You Make Changes)

```bash
zip function.zip lambda_function.py

aws lambda update-function-code \
  --function-name hr-claim-handler \
  --zip-file fileb://function.zip
```

---

## 📊 View Logs in CloudWatch (Optional)

```bash
aws logs describe-log-groups
aws logs describe-log-streams --log-group-name /aws/lambda/hr-claim-handler
```

---

## 🌍 Tip: Use a Region Flag (if needed)

```bash
--region us-west-2
```

