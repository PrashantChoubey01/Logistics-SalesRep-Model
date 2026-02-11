#!/usr/bin/env python3
"""
Test Claude API Connection
Tests if Claude API key is working and can make basic calls.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_claude_direct():
    """Test Claude API using Anthropic SDK directly"""
    print("=" * 60)
    print("TEST 1: Direct Anthropic SDK Connection")
    print("=" * 60)
    
    try:
        from anthropic import Anthropic
        
        # Load API key from .env
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ ANTHROPIC_API_KEY not found in .env")
            return False
        
        print(f"✓ API Key loaded: {api_key[:20]}...")
        
        # Initialize client
        client = Anthropic(api_key=api_key)
        print("✓ Anthropic client initialized")
        
        # Make a simple test call
        print("\n📞 Making test API call...")
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say 'Hello from Claude!' and nothing else."}
            ]
        )
        
        response_text = message.content[0].text
        print(f"✅ Response: {response_text}")
        print(f"✓ Model: {message.model}")
        print(f"✓ Tokens used: {message.usage.input_tokens} in, {message.usage.output_tokens} out")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install: pip install anthropic python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_claude_langchain():
    """Test Claude API using LangChain ChatAnthropic"""
    print("\n" + "=" * 60)
    print("TEST 2: LangChain ChatAnthropic Connection")
    print("=" * 60)
    
    try:
        from langchain_anthropic import ChatAnthropic
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("❌ ANTHROPIC_API_KEY not found in .env")
            return False
        
        print(f"✓ API Key loaded: {api_key[:20]}...")
        
        # Initialize LangChain client
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=0.1,
            max_tokens=100,
            anthropic_api_key=api_key
        )
        print("✓ ChatAnthropic client initialized")
        
        # Make a test call
        print("\n📞 Making test API call...")
        response = llm.invoke("Say 'Hello from LangChain Claude!' and nothing else.")
        
        print(f"✅ Response: {response.content}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install: pip install langchain-anthropic")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_claude_with_tools():
    """Test Claude API with function calling (tools)"""
    print("\n" + "=" * 60)
    print("TEST 3: Claude with Tool/Function Calling")
    print("=" * 60)
    
    try:
        from anthropic import Anthropic
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        client = Anthropic(api_key=api_key)
        
        # Define a simple tool
        tools = [
            {
                "name": "get_weather",
                "description": "Get the weather for a location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Temperature unit"
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
        
        print("✓ Tool schema defined")
        
        # Make API call with tools
        print("\n📞 Making API call with tool...")
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            tools=tools,
            messages=[
                {"role": "user", "content": "What's the weather in San Francisco?"}
            ]
        )
        
        print(f"✅ Response received")
        print(f"✓ Stop reason: {message.stop_reason}")
        
        # Check if tool was used
        if message.stop_reason == "tool_use":
            for content in message.content:
                if content.type == "tool_use":
                    print(f"✓ Tool called: {content.name}")
                    print(f"✓ Tool input: {content.input}")
        else:
            print(f"✓ Text response: {message.content[0].text if message.content else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n🧪 Testing Claude API Connection")
    print("=" * 60)
    
    results = []
    
    # Test 1: Direct Anthropic SDK
    results.append(("Direct Anthropic SDK", test_claude_direct()))
    
    # Test 2: LangChain
    results.append(("LangChain ChatAnthropic", test_claude_langchain()))
    
    # Test 3: Function calling
    results.append(("Claude with Tools", test_claude_with_tools()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Claude API is working correctly.")
        print("\n✅ You can now use Claude in your agents!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 Make sure:")
        print("   1. ANTHROPIC_API_KEY is set in .env")
        print("   2. pip install anthropic langchain-anthropic python-dotenv")
        print("   3. Your API key is valid and has credits")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
