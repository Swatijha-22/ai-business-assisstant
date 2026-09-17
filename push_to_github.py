#!/usr/bin/env python3
"""
GitHub Push Helper for AI Business Assistant

This script helps you authenticate and push to your GitHub repository.
"""

import subprocess
import sys
import getpass

def run_command(command, cwd=None):
    """Run a command and return result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 AI Business Assistant - GitHub Push Helper")
    print("=" * 50)
    
    print("\n📋 Your project is ready to push to GitHub!")
    print("Repository: https://github.com/Swatijha-22/ai-business-assisstant")
    
    print("\n🔐 Authentication Required")
    print("You have a few options:")
    
    print("\n1️⃣ OPTION 1: Use Personal Access Token (Recommended)")
    print("   - Go to: https://github.com/settings/tokens")
    print("   - Click 'Generate new token (classic)'")
    print("   - Select scopes: 'repo' (full control of private repositories)")
    print("   - Copy the token")
    print("   - Use it as password when Git asks")
    
    print("\n2️⃣ OPTION 2: Update Git credentials")
    print("   - Go to Windows Credential Manager")
    print("   - Find 'git:https://github.com' entry")
    print("   - Update username to 'Swatijha-22'")
    print("   - Update password to your GitHub password or token")
    
    print("\n3️⃣ OPTION 3: Use SSH (Advanced)")
    print("   - Set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh")
    print("   - Update remote URL: git remote set-url origin git@github.com:Swatijha-22/ai-business-assisstant.git")
    
    choice = input("\nWhich option would you like to try? (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🔑 Using Personal Access Token:")
        print("1. Generate token at: https://github.com/settings/tokens")
        print("2. Run: git push -u origin main")
        print("3. Username: Swatijha-22")
        print("4. Password: [paste your token]")
        
    elif choice == "2":
        print("\n🔑 Updating Git credentials:")
        print("1. Open Windows Credential Manager")
        print("2. Find and edit 'git:https://github.com'")
        print("3. Set username: Swatijha-22")
        print("4. Set password: [your GitHub password or token]")
        print("5. Run: git push -u origin main")
        
    elif choice == "3":
        print("\n🔑 Setting up SSH:")
        print("1. Generate SSH key: ssh-keygen -t ed25519 -C 'swatijha2022@vitbhopal.ac.in'")
        print("2. Add to GitHub: https://github.com/settings/ssh/new")
        print("3. Update remote: git remote set-url origin git@github.com:Swatijha-22/ai-business-assisstant.git")
        print("4. Push: git push -u origin main")
    
    else:
        print("Invalid choice. Please run the script again.")
        return
    
    print(f"\n✅ After authentication, run:")
    print(f"   git push -u origin main")
    print(f"\n🎉 Your AI Business Assistant will be live on GitHub!")
    print(f"📊 Repository URL: https://github.com/Swatijha-22/ai-business-assisstant")

if __name__ == "__main__":
    main()