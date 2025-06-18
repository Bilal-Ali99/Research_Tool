#!/usr/bin/env python3
"""
Setup script for Research Tool
Run this to install all required dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 Setting up Research Tool Dependencies...")
    print("=" * 50)
    
    # List of required packages
    packages = [
        "streamlit>=1.28.0",
        "langchain>=0.1.0", 
        "langchain-community>=0.0.20",
        "langchain-google-genai>=1.0.0",
        "google-generativeai>=0.3.0",
        "faiss-cpu>=1.7.4",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "requests>=2.31.0",
        "urllib3>=1.26.0"
    ]
    
    failed_packages = []
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        if not install_package(package):
            failed_packages.append(package)
    
    print("\n" + "=" * 50)
    
    if failed_packages:
        print("❌ Some packages failed to install:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n💡 Try installing them manually with:")
        print(f"   pip install {' '.join(failed_packages)}")
        return False
    else:
        print("✅ All packages installed successfully!")
        print("\n🚀 You can now run the Research Tool with:")
        print("   streamlit run main.py")
        return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)