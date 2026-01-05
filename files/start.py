#!/usr/bin/env python3
"""
Quick start script for FlyKnight
Checks dependencies and launches the game
"""

import sys
import subprocess

def check_pygame():
    """Check if pygame is installed"""
    try:
        import pygame
        print(f"✓ Pygame {pygame.version.ver} is installed")
        return True
    except ImportError:
        print("✗ Pygame is not installed")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False

def main():
    """Main entry point"""
    print("=" * 50)
    print("FlyKnight - Insect Knight Dungeon Crawler")
    print("=" * 50)
    print()
    
    # Check dependencies
    if not check_pygame():
        response = input("\nWould you like to install dependencies now? (y/n): ")
        if response.lower() == 'y':
            if not install_dependencies():
                print("\nPlease install pygame manually:")
                print("  pip install pygame")
                sys.exit(1)
        else:
            print("\nPlease install pygame before running:")
            print("  pip install pygame")
            sys.exit(1)
    
    print("\nStarting FlyKnight...\n")
    
    # Import and run
    from main import main as game_main
    game_main()

if __name__ == "__main__":
    main()
