---
sidebar_position: 2
---

# Installation

This guide will help you install Interview Corvus on your operating system.

## Prerequisites

Before installing, make sure you have:

- **OpenAI API key** (GPT-4 or GPT-4o recommended) OR **Anthropic API key**
- **Python 3.11+** (if building from source)
- Sufficient disk space for the application

## Download Options

You can get Interview Corvus in two ways:

1. **Download pre-built release** (Recommended) - Get the latest version from the [Releases page](https://github.com/afaneor/interview-corvus/releases)
2. **Build from source** - Clone the repository and build it yourself

## Platform-Specific Installation

### macOS

1. **Download** the latest `.dmg` file from the [Releases page](https://github.com/afaneor/interview-corvus/releases)

2. **Open** the `.dmg` file

3. **Drag** the `Interview Corvus.app` to your Applications folder

4. **First Launch**: Right-click on the app and select "Open" to bypass Gatekeeper

5. **Grant Permissions**: You'll need to allow:
   - **Screen Recording** - For taking screenshots of coding problems
   - **Accessibility** - For global hotkeys functionality
   - **Keychain Access** - For securely storing your API key

To grant these permissions manually:
- Go to **System Preferences → Security & Privacy → Privacy**
- Select each permission type and add Interview Corvus

### Windows

1. **Download** the latest `.zip` file for Windows from the [Releases page](https://github.com/afaneor/interview-corvus/releases)

2. **Extract** the contents to a location of your choice

3. **Run** `Interview Corvus.exe`

4. **Administrator Access**: You may need to run as administrator for some features

:::tip
If Windows Defender or your antivirus flags the application, you may need to add an exception. This is common for unsigned applications.
:::

### Linux

Linux support is available when building from source. Follow the instructions in the "Building from Source" section below.

## Building from Source

If you prefer to build Interview Corvus yourself:

```bash
# Clone the repository
git clone https://github.com/afaneor/interview-corvus.git
cd interview-corvus

# Install dependencies using Poetry
poetry install

# Run the application
poetry run python interview_corvus/main.py

# Build for your platform
poetry run python build.py
```

### Installing Poetry

If you don't have Poetry installed:

```bash
# On macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# On Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

## Initial Setup

After installation, follow these steps:

1. **Launch Interview Corvus**

2. **Open Settings** (File → Settings or click the Settings button)

3. **Configure API Provider**:
   - Select **OpenAI** or **Anthropic**
   - Enter your API key
   - Choose your preferred model (GPT-4o, Claude, etc.)

4. **Customize Settings** (Optional):
   - Set your preferred programming language
   - Adjust theme (Light/Dark)
   - Configure window opacity
   - Customize hotkeys

5. **Test the Setup**:
   - Take a test screenshot using the hotkey
   - Generate a solution to verify everything works

## Data Storage

Interview Corvus stores its data in the following locations:

- **macOS**: `~/.interview_corvus/`
- **Windows**: `%USERPROFILE%\.interview_corvus\`
- **Linux**: `~/.interview_corvus/`

This directory contains:
- Screenshots
- User settings
- Application configuration
- Chat history

## Troubleshooting

### macOS: Permission Issues

If the app won't take screenshots or respond to hotkeys:
1. Go to **System Preferences → Security & Privacy → Privacy**
2. Ensure Interview Corvus has permissions for Screen Recording and Accessibility

### Windows: Antivirus Blocking

If your antivirus blocks the application:
1. Add an exception for `Interview Corvus.exe`
2. Or temporarily disable the antivirus during installation

### API Key Not Saving

If your API key doesn't persist:
- **macOS**: Ensure Keychain Access permission is granted
- **Windows**: Run as administrator
- Check file permissions in the data storage directory

### Build Errors

If you encounter errors building from source:
```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --no-cache
```

## Next Steps

Now that you have Interview Corvus installed:

- Learn how to [use the application](./usage/getting-started.md)
- Explore [customization options](./customization/overview.md)
- Check out the [Web API](./api/overview.md)

## Uninstallation

To remove Interview Corvus:

1. **Delete the application**:
   - macOS: Remove from Applications folder
   - Windows: Delete the extracted folder

2. **Remove data** (optional):
   - Delete the data directory mentioned in the [Data Storage](#data-storage) section

3. **macOS only**: Remove keychain entry:
   - Open Keychain Access
   - Search for "interview-corvus"
   - Delete the entry
