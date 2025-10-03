---
sidebar_position: 2
---

# Installation Guide

This guide will walk you through the installation process for Interview Corvus on different platforms.

## Download Options

You can get Interview Corvus in two ways:

1. **Download pre-built releases** (Recommended for most users)
2. **Build from source** (For developers)

## Pre-built Releases

### macOS Installation

1. **Download** the latest `.dmg` file from the [Releases](https://github.com/afaneor/interview-corvus/releases) page
2. **Open** the `.dmg` file and drag `Interview Corvus.app` to your Applications folder
3. **Launch** the app - you may need to right-click and select "Open" to bypass Gatekeeper
4. **Grant permissions** when prompted:
   - **Screen Recording** - Required for taking screenshots
   - **Accessibility** - Required for global hotkeys
   - **Keychain Access** - For securely storing your API key

### Windows Installation

1. **Download** the latest `.zip` file for Windows from the [Releases](https://github.com/afaneor/interview-corvus/releases) page
2. **Extract** the contents to a location of your choice
3. **Run** `Interview Corvus.exe`
4. **Note**: You may need to run as administrator to enable some features

## Building from Source

### Prerequisites

- **Python 3.11+**
- **Poetry** (Python package manager)
- **Git**

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/afaneor/interview-corvus.git
cd interview-corvus

# Install dependencies
poetry install

# Run the application
poetry run python interview_corvus/main.py
```

### Building Executables

To build platform-specific executables:

```bash
# Build for your platform
poetry run python build.py
```

This will create executable files in the `dist/` directory.

## Required Permissions

### macOS Permissions

Interview Corvus requires the following permissions on macOS:

| Permission | Purpose | How to Grant |
|------------|---------|--------------|
| **Screen Recording** | Taking screenshots of coding problems | System Preferences → Security & Privacy → Privacy → Screen Recording |
| **Accessibility** | Global hotkeys when app is not in focus | System Preferences → Security & Privacy → Privacy → Accessibility |
| **Keychain Access** | Securely storing API keys | Automatically prompted by keyring library |

### Windows Permissions

- May require **administrator privileges** for some features
- **Firewall exceptions** may be needed for API communication

## Data Storage Locations

Interview Corvus stores its data in platform-specific locations:

- **macOS**: `~/.interview_corvus/`
- **Windows**: `%USERPROFILE%\.interview_corvus\`
- **Linux**: `~/.interview_corvus/`

This includes:
- Screenshots
- User settings
- Application data
- API configuration

## Troubleshooting

### Common Issues

**"App can't be opened" on macOS**
- Right-click the app and select "Open" instead of double-clicking
- Go to System Preferences → Security & Privacy → General and click "Open Anyway"

**Hotkeys not working**
- Ensure Accessibility permissions are granted
- Check if other applications are using the same hotkey combinations
- Try customizing hotkeys in the settings

**API connection issues**
- Verify your API key is correctly entered
- Check your internet connection
- Ensure your API provider account has sufficient credits

### Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/afaneor/interview-corvus/issues) page
2. Join the [Telegram Channel](https://t.me/pavlin_share) for community support
3. Create a new issue with detailed information about your problem

## Next Steps

Once installed, learn how to use Interview Corvus effectively:
- [Usage Guide](/docs/usage)
- [Hotkey Configuration](/docs/hotkeys)
- [Best Practices](/docs/best-practices)