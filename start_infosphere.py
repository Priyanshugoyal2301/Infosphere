"""
Infosphere Full-Stack Startup Script
===================================

This script ensures proper startup of both backend and frontend services
with robust error handling and health checks.
"""

import subprocess
import time
import requests
import os
import sys
from pathlib import Path
import threading
import json

def check_port_available(port):
    """Check if a port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def wait_for_service(url, timeout=60, service_name="Service"):
    """Wait for a service to become available"""
    print(f"🔄 Waiting for {service_name} to start...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} is running!")
                return True
        except:
            pass
        time.sleep(2)
    
    print(f"❌ {service_name} failed to start within {timeout} seconds")
    return False

def start_backend():
    """Start the backend service"""
    print("🚀 Starting Infosphere Backend...")
    
    backend_dir = Path("backend")
    venv_python = Path("venv/Scripts/python.exe")
    
    if not venv_python.exists():
        print("❌ Virtual environment not found! Please run: python -m venv venv")
        return False
    
    # Install dependencies if needed
    print("📦 Checking backend dependencies...")
    subprocess.run([
        str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"
    ], cwd=backend_dir, capture_output=True)
    
    # Start backend
    backend_process = subprocess.Popen([
        str(venv_python), "main.py"
    ], cwd=backend_dir)
    
    # Wait for backend to be ready
    if wait_for_service("http://localhost:8000/docs", service_name="Backend API"):
        return backend_process
    else:
        backend_process.terminate()
        return False

def start_frontend():
    """Start the frontend service"""
    print("🎨 Starting Infosphere Frontend...")
    
    frontend_dir = Path("frontend")
    
    # Install dependencies if needed
    print("📦 Installing frontend dependencies...")
    result = subprocess.run(["npm", "install"], cwd=frontend_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to install frontend dependencies: {result.stderr}")
        return False
    
    # Start frontend
    frontend_process = subprocess.Popen(["npm", "start"], cwd=frontend_dir)
    
    # Wait for frontend to be ready
    if wait_for_service("http://localhost:3000", service_name="Frontend App"):
        return frontend_process
    else:
        frontend_process.terminate()
        return False

def test_atie_integration():
    """Test ATIE API integration"""
    print("🧪 Testing ATIE Integration...")
    
    test_data = {
        "text": "This is a test of the fake news detection system.",
        "enable_cross_verification": True
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/atie/analyze-text",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            trust_score = result['data']['atie_trust_score']['score']
            print(f"✅ ATIE Integration Test Passed! Trust Score: {trust_score}")
            return True
        else:
            print(f"❌ ATIE Test Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ATIE Test Error: {e}")
        return False

def main():
    """Main startup function"""
    print("🌟 INFOSPHERE FULL-STACK STARTUP")
    print("=" * 50)
    
    # Check if ports are available
    if not check_port_available(8000):
        print("⚠️ Port 8000 is already in use (Backend)")
    if not check_port_available(3000):
        print("⚠️ Port 3000 is already in use (Frontend)")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend service")
        return False
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend service")
        backend_process.terminate()
        return False
    
    # Test ATIE integration
    if test_atie_integration():
        print("\n🎉 INFOSPHERE PLATFORM IS FULLY OPERATIONAL!")
        print("🌐 Frontend: http://localhost:3000")
        print("📡 Backend API: http://localhost:8000/docs")
        print("🔍 ATIE Service: Ready for AI-powered content verification")
        
        print("\n💡 Quick Test:")
        print("1. Go to http://localhost:3000")
        print("2. Click 'Media Verification'")
        print("3. Try text analysis with sample content")
        
        # Keep processes running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down services...")
            backend_process.terminate()
            frontend_process.terminate()
            print("✅ Services stopped successfully")
    else:
        print("❌ ATIE integration test failed")
        backend_process.terminate()
        frontend_process.terminate()
        return False

if __name__ == "__main__":
    main()