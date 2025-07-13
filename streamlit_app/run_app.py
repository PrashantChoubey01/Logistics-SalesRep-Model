"""Launch script for the Streamlit app"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def run_streamlit():
    """Run the Streamlit app"""
    try:
        subprocess.run([
            "streamlit", "run", "email_workflow_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped")
    except Exception as e:
        print(f"❌ Failed to run Streamlit: {e}")

if __name__ == "__main__":
    print("🚀 Starting Email Workflow Agent Streamlit App")
    
    # Change to app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    # Install requirements
    if install_requirements():
        # Run the app
        run_streamlit()
    else:
        print("❌ Failed to install requirements. Please install manually.")
        sys.exit(1)
