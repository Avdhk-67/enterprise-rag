import boto3
import json

client = boto3.client(service_name='bedrock-runtime')

prompt = "Hello Bedrock! Can you respond with a short message?"

response = client.invoke_model(
    modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 256,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })
)

response_body = json.loads(response["body"].read())
print(response_body)
