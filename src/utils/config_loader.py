"""Configuration loader for AWS and RAG settings."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_aws_config() -> Dict[str, Any]:
    """Load AWS configuration."""
    config_path = Path(__file__).parent.parent.parent / "config" / "aws_config.yaml"
    config = load_yaml_config(str(config_path))
    
    # Override with environment variables if present
    if os.getenv("AWS_ACCESS_KEY_ID"):
        config['aws']['credentials']['use_credentials_file'] = True
    if os.getenv("S3_BUCKET_NAME"):
        config['aws']['s3']['bucket_name'] = os.getenv("S3_BUCKET_NAME")
    if os.getenv("AWS_DEFAULT_REGION"):
        config['aws']['region'] = os.getenv("AWS_DEFAULT_REGION")
    
    return config['aws']


def get_rag_config() -> Dict[str, Any]:
    """Load RAG configuration."""
    config_path = Path(__file__).parent.parent.parent / "config" / "rag_config.yaml"
    config = load_yaml_config(str(config_path))
    return config['rag']


def get_env_var(key: str, default: Any = None) -> Any:
    """Get environment variable with optional default."""
    return os.getenv(key, default)

