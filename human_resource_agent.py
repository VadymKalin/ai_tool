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

# Attach role policy transcript
iam_client.attach_role_policy(
    RoleName="agent_role_name",
    PolicyArn=agent_bedrock_policy["Policy"]["Arn"]
)

# Creating the Amazon Bedrock agent
bedrock_agent_client = boto3.client('bedrock-agent')

response = bedrock_agent_client.create_agent(
    agentName="Human-Resource-Agent",
    description="this agent helps employees understanding company's policies \
    and requesting vacation time.",
    foundationModel="anthropic.claude-3-sonnet-20240229-v1:0",
    agentResourceRoleArn=agent_role["Role"]["Arn"],
    idleSessionTTLInSeconds=600,
    instruction="""You are a friendly agent that answers questions about company's 
    HR policies and helps employees to request vacation time off. You ALWAYS reply 
    politely and concise, using ONLY the available information in the company_policies 
    KNOWLEDGE_BASE or in the vacationHandler ACTION_GROUP.
    You should start with an acknowledgement of the employee's request and thanking 
    the employee for contacting you. Introduce yourself as the "HR AI Assistant". 
    ALWAYS mention your name as HR AI Assistant" in the first user interaction. 
    NEVER provide any information about available vacation days, company policies 
    and/or book any time off without first confirming the employee's id. NEVER 
    assume the employee id if it is not provided in the user prompt for you."""
)

# Preparing the agent
agent_id = response['agent']['agentId']
response = bedrock_agent_client.prepare_agent(
    agentId=agent_id
)
