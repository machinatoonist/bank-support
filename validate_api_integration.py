#!/usr/bin/env python3
"""
Build-time API validation script for Bank Support AI application.

This script validates that all required API integrations are working before deployment.
If any validation fails, the build process should fail to prevent broken deployments.

Run this script during the build process to ensure:
1. OpenAI API is accessible and working
2. Anthropic API is accessible and working  
3. A basic AI support request can be processed
4. All required environment variables are set
"""

import os
import sys
import asyncio
import json
from typing import Dict, Any
import traceback

def check_environment_variables() -> Dict[str, bool]:
    """Check that all required environment variables are set."""
    required_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
    }
    
    optional_vars = {
        'LOGFIRE_TOKEN': os.getenv('LOGFIRE_TOKEN'),
    }
    
    results = {}
    missing_required = []
    
    for var_name, value in required_vars.items():
        if value is None or value.strip() == '':
            results[var_name] = False
            missing_required.append(var_name)
        else:
            results[var_name] = True
            print(f"✅ {var_name}: Set")
    
    for var_name, value in optional_vars.items():
        if value is None or value.strip() == '':
            results[var_name] = False
            print(f"⚠️  {var_name}: Not set (optional)")
        else:
            results[var_name] = True
            print(f"✅ {var_name}: Set")
    
    if missing_required:
        print(f"\n❌ MISSING REQUIRED ENVIRONMENT VARIABLES: {', '.join(missing_required)}")
        print("Please set these environment variables before deployment.")
        return False
    
    return True

async def test_openai_api() -> bool:
    """Test OpenAI API connectivity."""
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Simple test request
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o-mini",  # Use cheaper model for testing
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10
        )
        
        if response and response.choices:
            print("✅ OpenAI API: Connected and working")
            return True
        else:
            print("❌ OpenAI API: Unexpected response format")
            return False
            
    except ImportError:
        print("❌ OpenAI API: openai package not installed")
        return False
    except Exception as e:
        print(f"❌ OpenAI API: Connection failed - {str(e)}")
        return False

async def test_anthropic_api() -> bool:
    """Test Anthropic API connectivity."""
    try:
        import anthropic
        
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Simple test request
        response = await asyncio.to_thread(
            client.messages.create,
            model="claude-3-haiku-20240307",  # Use cheaper model for testing
            max_tokens=10,
            messages=[{"role": "user", "content": "Test"}]
        )
        
        if response and response.content:
            print("✅ Anthropic API: Connected and working")
            return True
        else:
            print("❌ Anthropic API: Unexpected response format")
            return False
            
    except ImportError:
        print("❌ Anthropic API: anthropic package not installed")
        return False
    except Exception as e:
        print(f"❌ Anthropic API: Connection failed - {str(e)}")
        return False

async def test_bank_support_endpoint() -> bool:
    """Test the bank support AI endpoint with a real request."""
    try:
        # Import the FastAPI app
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test request
        payload = {
            "question": "What is my balance?",
            "customer_name": "Build Test User",
            "customer_id": 999
        }
        
        response = client.post("/support", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            required_fields = ['support_advice', 'block_card', 'risk', 'risk_explanation', 'risk_category']
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"❌ Bank Support API: Response missing fields: {missing_fields}")
                return False
            
            # Validate data types
            if not isinstance(data['risk'], (int, float)) or not (0 <= data['risk'] <= 10):
                print(f"❌ Bank Support API: Invalid risk value: {data['risk']}")
                return False
            
            print("✅ Bank Support API: AI endpoint working correctly")
            print(f"   Response: {data['support_advice'][:50]}...")
            return True
        else:
            print(f"❌ Bank Support API: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Bank Support API: Test failed - {str(e)}")
        traceback.print_exc()
        return False

async def main():
    """Run all validation tests."""
    print("🔍 Starting build-time API validation...\n")
    
    # 1. Check environment variables
    print("1. Checking environment variables...")
    env_ok = check_environment_variables()
    if not env_ok:
        print("\n❌ VALIDATION FAILED: Environment variables missing")
        sys.exit(1)
    
    print("\n2. Testing API connections...")
    
    # 2. Test OpenAI API
    openai_ok = await test_openai_api()
    
    # 3. Test Anthropic API  
    anthropic_ok = await test_anthropic_api()
    
    # 4. Test bank support endpoint
    print("\n3. Testing AI-powered bank support endpoint...")
    support_ok = await test_bank_support_endpoint()
    
    # Final results
    print("\n" + "="*50)
    print("BUILD VALIDATION RESULTS:")
    print("="*50)
    
    all_passed = env_ok and openai_ok and anthropic_ok and support_ok
    
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED - SAFE TO DEPLOY")
        print("✅ Environment variables configured")
        print("✅ OpenAI API working")
        print("✅ Anthropic API working") 
        print("✅ Bank Support AI endpoint working")
        print("\nThe application is ready for production deployment.")
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED - DO NOT DEPLOY")
        if not openai_ok:
            print("❌ OpenAI API not working")
        if not anthropic_ok:
            print("❌ Anthropic API not working")
        if not support_ok:
            print("❌ Bank Support AI endpoint not working")
        
        print("\nFix the issues above before attempting deployment.")
        print("This prevents deploying a broken application to users.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())