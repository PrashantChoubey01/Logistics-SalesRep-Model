#!/usr/bin/env python3
"""Check all available Claude models with your API key"""

from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Try all Claude models from newest to oldest
models_to_try = [
    # Claude 3.5 (newest)
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    
    # Claude 3 Opus (most powerful)
    "claude-3-opus-20240229",
    "claude-3-opus-latest",
    
    # Claude 3 Sonnet (balanced)
    "claude-3-sonnet-20240229",
    "claude-3-sonnet-latest",
    
    # Claude 3 Haiku (fastest/cheapest)
    "claude-3-haiku-20240307",
    "claude-3-haiku-latest",
    
    # Claude 2 (legacy)
    "claude-2.1",
    "claude-2.0",
]

print("🔍 Testing Claude Models with Your API Key")
print("=" * 70)
print("\nTesting from best to worst...\n")

working_models = []
failed_models = []

for model in models_to_try:
    try:
        print(f"Testing: {model:40s} ", end="", flush=True)
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"✅ WORKS!")
        working_models.append(model)
    except Exception as e:
        error_msg = str(e)[:60]
        print(f"❌ {error_msg}")
        failed_models.append((model, str(e)))

print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)

if working_models:
    print(f"\n✅ {len(working_models)} model(s) available:\n")
    for i, model in enumerate(working_models, 1):
        marker = "⭐ RECOMMENDED" if i == 1 else ""
        print(f"   {i}. {model} {marker}")
    
    print(f"\n💡 RECOMMENDATION:")
    print(f"   Use: {working_models[0]}")
    print(f"   This is the best model available with your API key.")
else:
    print("\n❌ No models available!")
    print("   Please check your API key or account status.")

print("\n" + "=" * 70)
