"""Setup script for initializing the project."""
import os
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "data/faiss_index",
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def check_env_file():
    """Check if .env file exists."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env file not found. Please copy .env.example to .env and configure it.")
        else:
            print("⚠️  .env file not found. Please create it with your AWS credentials.")
    else:
        print("✅ .env file found")


def main():
    """Run setup."""
    print("=" * 50)
    print("Enterprise RAG Project Setup")
    print("=" * 50)
    
    create_directories()
    check_env_file()
    
    print("\n" + "=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Configure .env file with your AWS credentials")
    print("2. Follow AWS_SETUP.md for AWS configuration")
    print("3. Run: python scripts/test_aws_connection.py")
    print("4. Install dependencies: pip install -r requirements.txt")
    print("5. Start the application: python app.py")


if __name__ == "__main__":
    main()

