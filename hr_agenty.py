#!/usr/bin/env python3

import json
import boto3
import botocore.exceptions

# Initialize AWS clients
iam_client = boto3.client("iam")
bedrock_agent_client = boto3.client("bedrock-agent")

# Define constants
POLICY_NAME = "hr-agent-bedrock-policy"
ROLE_NAME = "AmazonBedrockExecutionRoleForAgents_hr-agent"
FOUNDATION_MODEL_ARN = (
    "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
)

def create_iam_policy():
    policy_document = {
        "Version": "2025-07-17",
        "Statement": [
            {
                "Sid": "AmazonBedrockAgentBedrockFoundationModelPolicy",
                "Effect": "Allow",
                "Action": "bedrock:InvokeModel",
                "Resource": [FOUNDATION_MODEL_ARN]
            }
        ]
    }

    try:
        response = iam_client.create_policy(
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"IAM policy '{POLICY_NAME}' created.")
        return response["Policy"]["Arn"]
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"IAM policy '{POLICY_NAME}' already exists.")
        return f"arn:aws:iam::your-account-id:policy/{POLICY_NAME}"

def create_iam_role():
    assume_role_document = {
        "Version": "2025-07-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }]
    }

    try:
        response = iam_client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(assume_role_document)
        )
        print(f"IAM role '{ROLE_NAME}' created.")
        return response["Role"]["Arn"]
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"IAM role '{ROLE_NAME}' already exists.")
        role = iam_client.get_role(RoleName=ROLE_NAME)
        return role["Role"]["Arn"]

def attach_policy_to_role(policy_arn):
    try:
        iam_client.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn=policy_arn
        )
        print(f"Policy attached to role '{ROLE_NAME}'.")
    except Exception as e:
        print(f"Error attaching policy: {e}")

def create_bedrock_agent(role_arn):
    try:
        response = bedrock_agent_client.create_agent(
            agentName="Human-Resource-Agent",
            description="This agent helps employees understand company policies and request vacation time.",
            foundationModel="anthropic.claude-3-sonnet-20240229-v1:0",
            agentResourceRoleArn=role_arn,
            idleSessionTTLInSeconds=600,
            instruction="""You are a friendly agent that answers questions about company HR policies and helps employees request vacation time off. 
You ALWAYS reply politely and concisely, using ONLY the available information in the company_policies KNOWLEDGE_BASE or in the vacationHandler ACTION_GROUP.
Start by acknowledging the employee’s request and thanking them. Introduce yourself as the "HR First AI Assistant". 
ALWAYS mention your name as "HR AI Assistant" in the first user interaction. 
NEVER provide any information about available vacation days, company policies, or book any time off without first confirming the employee's ID. 
NEVER assume the employee ID if it is not provided."""
        )
        agent_id = response['agent']['agentId']
        print(f"Bedrock agent created with ID: {agent_id}")
        return agent_id
    except botocore.exceptions.ClientError as e:
        print(f"Failed to create Bedrock agent: {e}")
        return None

def prepare_agent(agent_id):
    try:
        bedrock_agent_client.prepare_agent(agentId=agent_id)
        print(f"Bedrock agent '{agent_id}' prepared.")
    except botocore.exceptions.ClientError as e:
        print(f"Failed to prepare agent: {e}")

def main():
    policy_arn = create_iam_policy()
    role_arn = create_iam_role()
    attach_policy_to_role(policy_arn)
    agent_id = create_bedrock_agent(role_arn)
    if agent_id:
        prepare_agent(agent_id)

if __name__ == "__main__":
    main()
