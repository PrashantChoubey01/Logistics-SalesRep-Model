#!/usr/bin/env python3
"""Check available Claude models"""

from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Try different model names
models_to_try = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-sonnet-latest",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229",
    "claude-3-haiku-20240307",
]

print("Testing Claude models...")
print("=" * 60)

for model in models_to_try:
    try:
        print(f"\nTrying: {model}")
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"✅ SUCCESS! Model {model} works!")
        print(f"   Response: {response.content[0].text}")
        break
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}")
