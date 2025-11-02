"""
Simple Infosphere Startup - Offline Ready
========================================

This version starts the application using offline-ready services.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def start_backend_offline():
    """Start backend with offline ATIE service"""
    
    # Temporarily replace the atie_service import
    backend_dir = Path("backend")
    services_dir = backend_dir / "services"
    
    # Create a simple atie_service.py that imports the offline version
    offline_wrapper = '''# Offline ATIE Service Wrapper
from .offline_atie_service import atie_service, get_textual_trust_score

# Re-export for compatibility
__all__ = ['atie_service', 'get_textual_trust_score']
'''
    
    with open(services_dir / "atie_service_wrapper.py", "w") as f:
        f.write(offline_wrapper)
    
    # Update the import in atie.py endpoints
    atie_endpoint = backend_dir / "api" / "v1" / "endpoints" / "atie.py"
    
    # Read the current file
    with open(atie_endpoint, "r") as f:
        content = f.read()
    
    # Replace the import
    content = content.replace(
        "from services.atie_service import atie_service, get_textual_trust_score",
        "from services.offline_atie_service import atie_service, get_textual_trust_score"
    )
    
    # Write back
    with open(atie_endpoint, "w") as f:
        f.write(content)
    
    print("✅ Configured for offline ATIE service")
    
    # Start the backend
    venv_python = Path("venv/Scripts/python.exe")
    
    process = subprocess.Popen([
        str(venv_python), "main.py"
    ], cwd=backend_dir)
    
    # Wait for it to start
    print("🚀 Starting backend...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000/docs", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is running!")
                return process
        except:
            pass
        time.sleep(1)
        print(f"⏳ Waiting for backend... ({i+1}/30)")
    
    print("❌ Backend failed to start")
    process.terminate()
    return None

def start_frontend():
    """Start the frontend"""
    frontend_dir = Path("frontend")
    
    print("🎨 Starting frontend...")
    process = subprocess.Popen(["npm", "start"], cwd=frontend_dir)
    
    # Wait for it to start
    for i in range(30):
        try:
            response = requests.get("http://localhost:3000", timeout=2)
            if response.status_code == 200:
                print("✅ Frontend is running!")
                return process
        except:
            pass
        time.sleep(1)
        print(f"⏳ Waiting for frontend... ({i+1}/30)")
    
    print("❌ Frontend failed to start")
    process.terminate()
    return None

def test_atie():
    """Test the ATIE service"""
    print("🧪 Testing ATIE service...")
    
    test_data = {
        "text": "This is a test of the offline fake news detection system.",
        "enable_cross_verification": False
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
            print(f"✅ ATIE Test Passed! Trust Score: {trust_score}")
            return True
        else:
            print(f"❌ ATIE Test Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ATIE Test Error: {e}")
        return False

def main():
    """Main function"""
    print("🌟 INFOSPHERE OFFLINE STARTUP")
    print("=" * 50)
    
    # Start backend
    backend_process = start_backend_offline()
    if not backend_process:
        return
    
    # Test ATIE
    if not test_atie():
        print("❌ ATIE service not working")
        backend_process.terminate()
        return
    
    # Start frontend  
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return
    
    print("\n🎉 INFOSPHERE IS READY!")
    print("🌐 Frontend: http://localhost:3000")
    print("📡 Backend: http://localhost:8000/docs")
    print("🔍 ATIE: Offline rule-based analysis ready")
    
    print("\n💡 Try this:")
    print("1. Go to http://localhost:3000")
    print("2. Click 'Media Verification'")
    print("3. Try 'Text Analysis' with: 'BREAKING: This is fake news!'")
    
    try:
        input("\nPress Enter to stop the services...")
    except KeyboardInterrupt:
        pass
    
    print("🛑 Stopping services...")
    backend_process.terminate()
    frontend_process.terminate()
    print("✅ Done!")

if __name__ == "__main__":
    main()