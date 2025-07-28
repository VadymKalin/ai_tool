import boto3
iam_client = boto3.client("iam")

# Create IAM policies for agent
bedrock_agent_bedrock_allow_policy_statement = {
    "Version": "2025-07-17",
    "Statement": [
        {
            "Sid": "AmazonBedrockAgentBedrockFoundationModelPolicy",
            "Effect": "Allow",
            "Action": "bedrock:InvokeModel",
            "Resource": [
                "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
            ]
        }
    ]
}

bedrock_policy_json = json.dumps(bedrock_agent_bedrock_allow_policy_statement) 
agent_bedrock_policy = iam_client.create_policy(
    PolicyName="hr-agent-bedrock-policy",
    PolicyDocument=bedrock_policy_json
)

# Create IAM Role for the agent and attach IAM policies
assume_role_policy_document = {
    "Version": "2025-07-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {
            "Service": "bedrock.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
    }]
}

agent_role_name = "AmazonBedrockExecutionRoleForAgents_hr-agent"
assume_role_policy_document_json = json.dumps(assume_role_policy_document)

agent_role = iam_client.create_role(
    RoleName=agent_role_name,
    AssumeRolePolicyDocument=assume_role_policy_document_json
)
