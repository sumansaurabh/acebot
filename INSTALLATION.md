# Installation Guide

This guide provides detailed instructions for installing Interview Corvus on different platforms.

## Prerequisites

Before installing Interview Corvus, ensure you have:

- **API Key**: OpenAI API key (GPT-4 or GPT-4o recommended) or Anthropic API key (Claude)
- **Python 3.11+**: Only required if building/running from source
- **Poetry**: Only required if building from source

## Installation Methods

### Method 1: Download Pre-built Binaries (Recommended)

The easiest way to get started is to download the pre-built application for your platform.

#### macOS

1. Visit the [Releases](https://github.com/afaneor/interview-corvus/releases) page
2. Download the latest `.dmg` file (e.g., `Interview_Corvus-0.2.3-macOS.dmg`)
3. Open the downloaded `.dmg` file
4. Drag the `Interview Corvus.app` to your Applications folder
5. Navigate to Applications and locate Interview Corvus
6. **First Launch**: Right-click on the app and select "Open" to bypass macOS Gatekeeper
7. Click "Open" in the security dialog

**Required Permissions (macOS)**:
- **Screen Recording**: Required for taking screenshots of coding problems
  - Go to System Preferences → Security & Privacy → Privacy → Screen Recording
  - Check the box next to Interview Corvus
- **Accessibility**: Required for global hotkeys to work when the app is not in focus
  - Go to System Preferences → Security & Privacy → Privacy → Accessibility
  - Check the box next to Interview Corvus
- **Keychain Access**: The app will prompt for keychain access to securely store your API key

#### Windows

1. Visit the [Releases](https://github.com/afaneor/interview-corvus/releases) page
2. Download the latest `.zip` file for Windows (e.g., `Interview_Corvus-0.2.3-Windows.zip`)
3. Extract the contents of the `.zip` file to a location of your choice (e.g., `C:\Program Files\Interview Corvus`)
4. Navigate to the extracted folder
5. Run `Interview Corvus.exe`

**Note**: You may need to run as administrator to enable some features like global hotkeys.

#### Linux

1. Visit the [Releases](https://github.com/afaneor/interview-corvus/releases) page
2. Download the latest `.tar.gz` file for Linux (e.g., `Interview_Corvus-0.2.3-Linux.tar.gz`)
3. Extract the archive:
   ```bash
   tar -xzvf Interview_Corvus-0.2.3-Linux.tar.gz
   ```
4. Navigate to the extracted directory:
   ```bash
   cd "Interview Corvus"
   ```
5. Run the application:
   ```bash
   ./Interview\ Corvus
   ```

**Required Dependencies (Linux)**:
- Qt6 libraries (usually pre-installed or included in the bundle)
- X11 or Wayland display server
- DBus SecretService (for secure API key storage)

### Method 2: Building from Source

Building from source gives you the latest development version and allows you to customize the application.

#### Prerequisites for Building

- Python 3.11, 3.12, or 3.13
- Poetry package manager
- Git

#### Step-by-Step Build Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/afaneor/interview-corvus.git
   cd interview-corvus
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install Dependencies**
   ```bash
   poetry install
   ```

4. **Run from Source** (for development/testing)
   ```bash
   poetry run python interview_corvus/main.py
   ```

5. **Build Executable** (optional)

   To build a standalone executable for your current platform:
   ```bash
   poetry run python build.py
   ```

   To build for a specific platform:
   ```bash
   # For macOS
   poetry run python build.py macos

   # For Windows
   poetry run python build.py windows

   # For Linux
   poetry run python build.py linux
   ```

   The built application will be available in the `dist/` directory.

#### Build Output Locations

- **macOS**: `dist/Interview_Corvus-{version}-macOS.dmg`
- **Windows**: `dist/Interview_Corvus-{version}-Windows.zip`
- **Linux**: `dist/Interview_Corvus-{version}-Linux.tar.gz`

## Initial Configuration

After installation, you need to configure the application:

1. **Launch Interview Corvus**
2. **Enter API Key**:
   - Click on "Settings" or go to File → Settings
   - Select your API provider (OpenAI or Anthropic)
   - Enter your API key
   - Click "Save" - your key will be securely stored in your system keychain
3. **Configure Preferences** (optional):
   - Choose your preferred theme (Light/Dark)
   - Set default programming language
   - Customize hotkeys if desired
   - Adjust window opacity and other UI settings

## Data Storage Locations

Interview Corvus stores user data in the following locations:

- **macOS**: `~/.interview_corvus/`
- **Windows**: `%USERPROFILE%\.interview_corvus\`
- **Linux**: `~/.interview_corvus/`

This directory contains:
- Screenshots
- User settings and preferences
- Application logs

## Troubleshooting

### macOS: "App can't be opened because it is from an unidentified developer"

Right-click on the app and select "Open" instead of double-clicking. Confirm that you want to open it.

### Windows: "Windows protected your PC" warning

Click "More info" and then "Run anyway". This happens because the application is not code-signed.

### Linux: Missing dependencies

Install required system packages:

```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt6 libxcb-xinerama0

# Fedora
sudo dnf install python3-qt6 libxcb

# Arch
sudo pacman -S python-pyqt6
```

### Global Hotkeys Not Working

- **macOS**: Ensure the app has Accessibility permissions (System Preferences → Security & Privacy → Privacy → Accessibility)
- **Windows**: Try running the application as administrator
- **Linux**: Some desktop environments may conflict with global hotkeys. Try customizing them in settings.

### Screenshot Feature Not Working

- **macOS**: Grant Screen Recording permission (System Preferences → Security & Privacy → Privacy → Screen Recording)
- **Windows/Linux**: Ensure the application has necessary display access permissions

## Uninstallation

### macOS
1. Delete the application from Applications folder
2. Remove data directory: `rm -rf ~/.interview_corvus/`
3. Remove keychain entry (optional)

### Windows
1. Delete the application folder
2. Remove data directory: Delete `%USERPROFILE%\.interview_corvus\`

### Linux
1. Delete the application folder
2. Remove data directory: `rm -rf ~/.interview_corvus/`

## Getting Help

If you encounter issues during installation:

1. Check the [Issues](https://github.com/afaneor/interview-corvus/issues) page on GitHub
2. Review the main [README.md](README.md) for additional information
3. Create a new issue with detailed information about your problem

## Next Steps

After installation, refer to the [README.md](README.md) for:
- Usage guide and best practices
- Hotkey customization
- Prompt template customization
- Contributing guidelines
