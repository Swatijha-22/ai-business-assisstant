#!/usr/bin/env python3
"""
API Endpoints Test

This script tests our authentication API endpoints to ensure they work correctly.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_user_registration():
    """Test user registration endpoint"""
    print("\n👤 Testing user registration...")
    
    user_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User registered successfully: {data['email']}")
            return True, data
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False, None

def test_user_login():
    """Test user login endpoint"""
    print("\n🔐 Testing user login...")
    
    login_data = {
        "email": "testuser@example.com", 
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful, token received")
            print(f"   Token type: {data['token_type']}")
            print(f"   Token preview: {data['access_token'][:50]}...")
            return True, data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False, None

def test_protected_endpoint(token):
    """Test protected endpoint with JWT token"""
    print("\n🔒 Testing protected endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Protected endpoint access successful")
            print(f"   User: {data['email']}")
            print(f"   Active: {data['is_active']}")
            return True
        else:
            print(f"❌ Protected endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Protected endpoint error: {e}")
        return False

def test_invalid_login():
    """Test login with invalid credentials"""
    print("\n🚫 Testing invalid login...")
    
    login_data = {
        "email": "testuser@example.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 401:
            print("✅ Invalid login correctly rejected")
            return True
        else:
            print(f"❌ Invalid login should have been rejected: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid login test error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 AI Business Assistant - API Endpoints Test")
    print("=" * 60)
    print("🔗 Testing against: http://localhost:8000")
    print("📝 Make sure the server is running: python run_server.py")
    print("=" * 60)
    
    success = True
    token = None
    
    # Test basic health check
    success &= test_health_check()
    
    # Test user registration
    reg_success, user_data = test_user_registration()
    success &= reg_success
    
    if reg_success:
        # Test user login
        login_success, access_token = test_user_login()
        success &= login_success
        
        if login_success:
            token = access_token
            # Test protected endpoint
            success &= test_protected_endpoint(token)
            
        # Test invalid login
        success &= test_invalid_login()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All API tests passed! Authentication system is fully functional.")
        print("\n✅ Your AI Business Assistant now supports:")
        print("   - User registration")
        print("   - JWT authentication")
        print("   - Protected endpoints")
        print("   - Proper error handling")
        print(f"\n📊 View API documentation: http://localhost:8000/docs")
    else:
        print("⚠️  Some API tests failed. Check the server logs.")
    
    return success

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready for Phase 3: Document Processing!")
    else:
        print("\n🔧 Fix authentication issues before continuing.")