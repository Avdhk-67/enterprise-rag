"""Test script to verify AWS connections."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.aws_client import get_s3_client, get_bedrock_client
from src.utils.config_loader import get_aws_config, get_env_var


def test_s3_connection():
    """Test S3 connection and bucket access."""
    print("Testing S3 connection...")
    try:
        s3_client = get_s3_client()
        config = get_aws_config()
        bucket_name = get_env_var("S3_BUCKET_NAME", config.get("s3", {}).get("bucket_name"))
        
        # Try to list bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
        print(f"✅ S3 connection successful! Bucket: {bucket_name}")
        return True
    except Exception as e:
        print(f"❌ S3 connection failed: {str(e)}")
        return False


def test_bedrock_connection():
    """Test Bedrock connection and model access by doing a small inference."""
    import json
    import botocore.exceptions
    
    print("\nTesting Bedrock connection...")
    try:
        bedrock_client = get_bedrock_client()
        config = get_aws_config()
        model_id = config.get("bedrock", {}).get("models", {}).get("generation", {}).get("model_id")

        test_input = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 20,
            "messages": [
             {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hello from test script!"
                }
            ]
        }
    ],
    "max_tokens": 20
}


        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(test_input),
            contentType="application/json"
        )

        print(f"✅ Bedrock connection successful! Model: {model_id}")
        return True

    except botocore.exceptions.ClientError as e:
        print(f"❌ Bedrock client error: {e}")
        return False
    except Exception as e:
        print(f"❌ Bedrock connection failed: {e}")
        return False



def test_vector_db_connection():
    """Test vector database connection."""
    print("\nTesting Vector Database connection...")
    try:
        from src.retrieval.vector_store import get_vector_store
        vector_store = get_vector_store()
        print(f"✅ Vector store initialized! Type: {type(vector_store).__name__}")
        return True
    except Exception as e:
        print(f"❌ Vector database connection failed: {str(e)}")
        return False


def main():
    """Run all connection tests."""
    print("=" * 50)
    print("AWS Connection Test")
    print("=" * 50)
    
    results = []
    results.append(("S3", test_s3_connection()))
    results.append(("Bedrock", test_bedrock_connection()))
    results.append(("Vector DB", test_vector_db_connection()))
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for service, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{service}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All connections successful!")
    else:
        print("\n⚠️  Some connections failed. Please check AWS_SETUP.md for configuration help.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

