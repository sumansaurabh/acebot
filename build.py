#!/usr/bin/env python
"""
Build script for Interview Corvus application for various operating systems.
Usage: poetry run python build.py

This script automates the build process for Interview Corvus, including cleaning build directories, checking dependencies, and packaging the application for macOS, Windows, and Linux. It uses PyInstaller for creating executables and handles platform-specific packaging (DMG for macOS, ZIP for Windows, TGZ for Linux).
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_dirs():
    """
    Clean build directories ('build' and 'dist').
    Removes previous build artifacts to ensure a clean build environment.
    """
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Directory cleaned: {dir_name}")


def get_version():
    """
    Retrieve the application version from the module.
    Returns the version string if available, otherwise returns 'dev'.
    """
    sys.path.append(os.path.abspath("."))
    try:
        from interview_corvus import __version__

        return __version__
    except ImportError:
        print("Could not import version. Using 'dev'.")
        return "dev"


def build_macos():
    """
    Build Interview Corvus for macOS.
    Uses PyInstaller to create a macOS app bundle and packages it into a DMG image.
    """
    print("\n=== Building for macOS ===")
    version = get_version()

    # Create temporary directory for the app
    app_name = "Interview Corvus.app"
    if os.path.exists(f"dist/{app_name}"):
        shutil.rmtree(f"dist/{app_name}")

    # Run PyInstaller
    cmd = [
        "pyinstaller",
        "--clean",
        "--windowed",
        "--name=Interview Corvus",
        "--add-data=resources:resources",
        "--hidden-import=PyQt6.QtSvg",
        "--hidden-import=tiktoken_ext.openai_public",
        "--hidden-import=tiktoken_ext",
        "--hidden-import=keyring.backends.macOS",
        "--osx-bundle-identifier=com.interview.corvus",
        "interview_corvus/main.py",
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.SubprocessError as e:
        print(f"Error during macOS build: {e}")
        return

    # Create DMG image
    print("Creating DMG image...")
    dmg_name = f"Interview_Corvus-{version}-macOS.dmg"

    try:
        subprocess.run(
            [
                "hdiutil",
                "create",
                "-volname",
                f"Interview Corvus {version}",
                "-srcfolder",
                f"dist/{app_name}",
                "-ov",
                "-format",
                "UDZO",
                f"dist/{dmg_name}",
            ],
            check=True,
        )
        print(f"macOS build completed: dist/{dmg_name}")
    except subprocess.SubprocessError as e:
        print(f"Error creating DMG: {e}")
        print(f"Build is available in directory: dist/{app_name}")


def build_windows():
    """
    Build Interview Corvus for Windows.
    Uses PyInstaller to create a Windows executable and packages it into a ZIP archive.
    """
    print("\n=== Building for Windows ===")
    version = get_version()

    # Use correct separator for Windows
    add_data_param = (
        "resources;resources"
        if platform.system() == "Windows"
        else "resources:resources"
    )

    cmd = [
        "pyinstaller",
        "--clean",
        "--windowed",
        "--name=Interview Corvus",
        f"--add-data={add_data_param}",
        "--hidden-import=PyQt6.QtSvg",
        "--hidden-import=tiktoken_ext.openai_public",
        "--hidden-import=tiktoken_ext",
        "--hidden-import=keyring.backends.Windows",
        "interview_corvus/main.py",
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.SubprocessError as e:
        print(f"Error during Windows build: {e}")
        return

    # Create ZIP archive
    print("Creating ZIP archive...")
    output_dir = "dist/Interview Corvus"
    zip_name = f"Interview_Corvus-{version}-Windows.zip"

    try:
        shutil.make_archive(
            base_name=f"dist/{zip_name.replace('.zip', '')}",
            format="zip",
            root_dir="dist",
            base_dir="Interview Corvus",
        )
        print(f"Windows build completed: dist/{zip_name}")
    except Exception as e:
        print(f"Error creating ZIP archive: {e}")
        print(f"Build is available in directory: {output_dir}")


def build_linux():
    """
    Build Interview Corvus for Linux.
    Uses PyInstaller to create a Linux executable and packages it into a TGZ archive.
    """
    print("\n=== Building for Linux ===")
    version = get_version()

    # Run PyInstaller
    cmd = [
        "pyinstaller",
        "--clean",
        "--windowed",
        "--name=Interview Corvus",  # Unified name for all platforms
        "--add-data=resources:resources",
        "--hidden-import=PyQt6.QtSvg",
        "--hidden-import=tiktoken_ext.openai_public",
        "--hidden-import=tiktoken_ext",
        "--hidden-import=keyring.backends.SecretService",
        "interview_corvus/main.py",
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.SubprocessError as e:
        print(f"Error during Linux build: {e}")
        return

    # Create TGZ archive
    print("Creating TGZ archive...")
    output_dir = "dist/Interview Corvus"
    tgz_name = f"Interview_Corvus-{version}-Linux.tar.gz"

    try:
        subprocess.run(
            ["tar", "-czvf", f"dist/{tgz_name}", "-C", "dist", "Interview Corvus"],
            check=True,
        )
        print(f"Linux build completed: dist/{tgz_name}")
    except subprocess.SubprocessError as e:
        print(f"Error creating TGZ archive: {e}")
        print(f"Build is available in directory: {output_dir}")


def check_dependencies():
    """
    Check for required dependencies (currently only PyInstaller).
    Prints a warning if any dependencies are missing.
    Returns True if all dependencies are present, False otherwise.
    """
    missing_deps = []

    # Check PyInstaller
    try:
        subprocess.run(
            ["pyinstaller", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        missing_deps.append("PyInstaller")

    if missing_deps:
        print("\nWARNING: The following dependencies are missing:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("Please install them before building.")
        return False

    return True


def main():
    """
    Main entry point for the build script.
    Detects the current OS, checks dependencies, cleans previous builds, and triggers the appropriate build process.
    """
    current_os = platform.system()

    print("=== Interview Corvus Build ===")
    print(f"Current OS: {current_os}")
    print(f"Application version: {get_version()}")

    # Create resources directory if it does not exist
    Path("resources").mkdir(exist_ok=True)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Clean previous builds
    clean_build_dirs()

    # Determine which build to run
    if len(sys.argv) > 1:
        target_os = sys.argv[1].lower()
        if target_os == "macos" or target_os == "darwin":
            build_macos()
        elif target_os == "windows" or target_os == "win":
            build_windows()
        elif target_os == "linux":
            build_linux()
        else:
            print(f"Unknown OS: {target_os}")
            print("Use: macos, windows, or linux")
    else:
        # If OS is not specified, build for the current OS
        if current_os == "Darwin":
            build_macos()
        elif current_os == "Windows":
            build_windows()
        elif current_os == "Linux":
            build_linux()
        else:
            print(f"Unsupported OS for automatic build: {current_os}")
            print("Please specify the OS manually: macos, windows, or linux")


if __name__ == "__main__":
    main()
