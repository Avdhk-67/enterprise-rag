"""AWS client initialization and utilities."""
import boto3
from typing import Optional
from botocore.config import Config
from src.utils.config_loader import get_aws_config, get_env_var


def get_s3_client():
    """Initialize and return S3 client."""
    config = get_aws_config()
    region = get_env_var("AWS_DEFAULT_REGION", config.get("region", "us-east-1"))
    
    # Use IAM role if available, otherwise use credentials
    if config.get("credentials", {}).get("use_iam_role", False):
        return boto3.client('s3', region_name=region)
    else:
        return boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=get_env_var("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_env_var("AWS_SECRET_ACCESS_KEY")
        )


def get_bedrock_client():
    """Initialize and return Bedrock client."""
    config = get_aws_config()
    region = get_env_var("AWS_DEFAULT_REGION", config.get("bedrock", {}).get("region", "us-east-1"))
    
    # Configure for Bedrock
    bedrock_config = Config(
        region_name=region,
        retries={
            'max_attempts': 10,
            'mode': 'standard'
        }
    )
    
    if config.get("credentials", {}).get("use_iam_role", False):
        return boto3.client('bedrock-runtime', config=bedrock_config)
    else:
        return boto3.client(
            'bedrock-runtime',
            config=bedrock_config,
            aws_access_key_id=get_env_var("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_env_var("AWS_SECRET_ACCESS_KEY")
        )


def get_bedrock_agent_client():
    """Initialize and return Bedrock Agent client (for planning)."""
    config = get_aws_config()
    region = get_env_var("AWS_DEFAULT_REGION", config.get("bedrock", {}).get("region", "us-east-1"))
    
    if config.get("credentials", {}).get("use_iam_role", False):
        return boto3.client('bedrock-agent-runtime', region_name=region)
    else:
        return boto3.client(
            'bedrock-agent-runtime',
            region_name=region,
            aws_access_key_id=get_env_var("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=get_env_var("AWS_SECRET_ACCESS_KEY")
        )

