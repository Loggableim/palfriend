#!/usr/bin/env python3
"""
Validation script for PalFriend launcher build system.
Checks that all necessary files and configurations are in place.
"""

import os
import sys


def check_python_version():
    """Check that Python version is compatible with build requirements."""
    version = sys.version_info
    status = "✓"
    if version[:2] >= (3, 13):
        status = "✗"
        print(f"{status} Python version: {version.major}.{version.minor}.{version.micro} (INCOMPATIBLE)")
        print("    ERROR: Python 3.13+ is not supported by PyInstaller and required dependencies")
        print("    Please use Python 3.12.x or 3.11.x for building")
        return False
    elif version[:2] < (3, 11):
        status = "⚠"
        print(f"{status} Python version: {version.major}.{version.minor}.{version.micro} (OLD)")
        print("    Warning: Python 3.11 or 3.12 is recommended")
        return True
    else:
        print(f"{status} Python version: {version.major}.{version.minor}.{version.micro} (compatible)")
        return True


def check_file(path, description):
    """Check if a file exists."""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists


def check_content(path, search_text, description):
    """Check if a file contains specific text."""
    if not os.path.exists(path):
        print(f"✗ {description}: {path} (file not found)")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            found = search_text in content
            status = "✓" if found else "✗"
            print(f"{status} {description}")
            return found
    except UnicodeDecodeError as e:
        print(f"✗ {description}: {path} (encoding error: {e})")
        return False
    except Exception as e:
        print(f"✗ {description}: {path} (error: {e})")
        return False


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("PalFriend Launcher Build System Validation")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Check Python version first
    print("Checking Python version...")
    all_passed &= check_python_version()
    print()
    
    # Check core files
    print("Checking core files...")
    all_passed &= check_file("launcher.py", "Launcher entry point")
    all_passed &= check_file("bootstrap_launcher.py", "Bootstrapper entry point")
    check_file("palfriend-launcher.spec", "Legacy PyInstaller spec file (optional)")
    all_passed &= check_file("palfriend.spec", "Main app PyInstaller spec file")
    all_passed &= check_file("palfriendlauncher.spec", "Bootstrapper PyInstaller spec file")
    all_passed &= check_file("build_launcher.bat", "Windows build script")
    all_passed &= check_file("build_launcher.sh", "Linux/Mac build script")
    all_passed &= check_file("BUILD_LAUNCHER.md", "Build documentation")
    print()
    
    # Check application files
    print("Checking application files...")
    all_passed &= check_file("app.py", "Flask app")
    all_passed &= check_file("main.py", "Main application")
    all_passed &= check_file("settings.py", "Settings module")
    all_passed &= check_file("requirements.txt", "Requirements file")
    print()
    
    # Check workflow
    print("Checking GitHub Actions workflow...")
    all_passed &= check_file(".github/workflows/build_launcher.yml", "Build workflow")
    all_passed &= check_content(
        ".github/workflows/build_launcher.yml",
        "palfriend.spec",
        "Workflow builds palfriend.exe"
    )
    all_passed &= check_content(
        ".github/workflows/build_launcher.yml",
        "palfriendlauncher.spec",
        "Workflow builds palfriendlauncher.exe"
    )
    print()
    
    # Check spec file content
    print("Checking spec file configuration...")
    all_passed &= check_content(
        "palfriend.spec",
        "launcher.py",
        "Main spec references launcher.py"
    )
    all_passed &= check_content(
        "palfriend.spec",
        "hiddenimports",
        "Main spec defines hidden imports"
    )
    all_passed &= check_content(
        "palfriend.spec",
        "datas",
        "Main spec defines data files"
    )
    all_passed &= check_content(
        "palfriendlauncher.spec",
        "bootstrap_launcher.py",
        "Bootstrapper spec references bootstrap_launcher.py"
    )
    print()
    
    # Check launcher.py
    print("Checking launcher.py implementation...")
    all_passed &= check_content(
        "launcher.py",
        "from app import main",
        "Launcher imports app.main"
    )
    all_passed &= check_content(
        "launcher.py",
        "webbrowser",
        "Launcher opens browser"
    )
    print()
    
    # Check app.py
    print("Checking app.py compatibility...")
    all_passed &= check_content(
        "app.py",
        "def main()",
        "app.py has main() function"
    )
    all_passed &= check_content(
        "app.py",
        "frozen",
        "app.py handles PyInstaller mode"
    )
    print()
    
    # Check .gitignore
    print("Checking .gitignore configuration...")
    all_passed &= check_content(
        ".gitignore",
        "build/",
        ".gitignore excludes build directory"
    )
    all_passed &= check_content(
        ".gitignore",
        "dist/",
        ".gitignore excludes dist directory"
    )
    print()
    
    # Check modules directory
    print("Checking modules directory...")
    all_passed &= check_file("modules/__init__.py", "Modules package")
    all_passed &= check_file("modules/tts.py", "TTS module")
    all_passed &= check_file("modules/audio.py", "Audio module")
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("✓ All validation checks passed!")
        print()
        print("Next steps:")
        print("1. Run build_launcher.bat (Windows) or build_launcher.sh (Linux/Mac)")
        print("2. Or create a PR to trigger the GitHub Actions workflow")
        print("3. Test the generated executables:")
        print("   - dist/palfriend/palfriend.exe (main app)")
        print("   - dist/palfriendlauncher.exe (bootstrapper)")
        return 0
    else:
        print("✗ Some validation checks failed!")
        print("Please review the errors above and fix them.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
