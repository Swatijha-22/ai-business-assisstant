#!/usr/bin/env python3
"""
Git Setup Script for AI Business Assistant

This script will help you initialize Git and push to GitHub once you have disk space available.
"""

import subprocess
import sys
import os

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {command}")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {command}")
        print(f"   Exception: {e}")
        return False

def check_disk_space():
    """Check if we have enough disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free / (1024**3)
        print(f"💾 Available disk space: {free_gb:.2f} GB")
        return free_gb > 0.5  # Need at least 500MB
    except Exception as e:
        print(f"⚠️  Could not check disk space: {e}")
        return False

def setup_git():
    """Set up Git repository and push to GitHub"""
    print("🚀 AI Business Assistant - Git Setup")
    print("=" * 50)
    
    # Check disk space
    if not check_disk_space():
        print("❌ Insufficient disk space. Please free up at least 500MB and try again.")
        print("\n💡 To free up space, try:")
        print("   - Empty the Recycle Bin")
        print("   - Clear temporary files (Run -> %temp%)")
        print("   - Clear browser cache")
        print("   - Uninstall unused programs")
        return False
    
    print("\n📁 Initializing Git repository...")
    if not run_command("git init"):
        return False
    
    print("\n📝 Adding initial commit...")
    if not run_command("git add ."):
        return False
    
    if not run_command('git commit -m "Initial commit: AI Business Assistant project structure"'):
        return False
    
    print("\n🌿 Creating main branch...")
    run_command("git branch -M main")
    
    print("\n🔗 Instructions for GitHub setup:")
    print("1. Go to https://github.com/new")
    print("2. Create a repository named 'ai-business-assistant'")
    print("3. Don't initialize with README (we already have one)")
    print("4. Copy the repository URL")
    print("5. Run these commands:")
    print("   git remote add origin <your-repo-url>")
    print("   git push -u origin main")
    
    print("\n🎉 Git setup complete! Your project is ready to push to GitHub.")
    return True

if __name__ == "__main__":
    success = setup_git()
    if not success:
        sys.exit(1)