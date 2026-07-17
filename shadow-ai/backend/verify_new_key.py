import os
from openai import OpenAI
from dotenv import load_dotenv

# Load from .env file
load_dotenv(r"c:\Users\gokul\OneDrive\Pictures\Attachments\Documents\GK_workspace\shadow-ai\backend\.env")

def verify_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment.")
        return False
    print(f"Testing key: {api_key[:10]}...")
    
    client = OpenAI(api_key=api_key, base_url="https://api.ai.cc/v1")
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "user", "content": "Say 'Neural link established' if you can read this."}],
            max_tokens=20
        )
        print("Success!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    verify_key()
