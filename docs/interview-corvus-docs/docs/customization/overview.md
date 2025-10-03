---
sidebar_position: 1
---

# Customization Overview

Interview Corvus is highly customizable to fit your workflow and preferences. This section covers all customization options available.

## Accessing Settings

Open the settings dialog:

**Methods:**
1. Click the **Settings** button in the main window
2. Use menu: **File → Settings**
3. Right-click the system tray icon (if available)

Settings are organized into tabs for easy navigation.

## What Can Be Customized?

### User Interface
- Theme (Light/Dark)
- Window opacity
- Font size
- Always on top
- Window position

### AI Configuration
- API provider (OpenAI/Anthropic)
- Model selection
- Temperature setting
- API key management

### Programming
- Default programming language
- Code style preferences
- Output format

### Hotkeys
- All keyboard shortcuts
- Platform-specific defaults
- Custom key combinations

### Prompts
- Solution generation template
- Optimization template
- Complexity analysis template
- Screenshot analysis template

### Web Server
- Auto-start on launch
- Port configuration
- Host settings

## Quick Customization Guide

### For Beginners

Start with these essential settings:

1. **API Key** - Set your OpenAI or Anthropic key
2. **Default Language** - Choose your primary programming language
3. **Theme** - Select Light or Dark mode
4. **Basic Hotkeys** - Learn the screenshot and solution hotkeys

### For Power Users

Advanced customization options:

1. **Custom Hotkeys** - Optimize for your keyboard layout
2. **Prompt Templates** - Fine-tune AI output
3. **Model Selection** - Choose optimal models for speed/quality
4. **Window Behavior** - Configure opacity and positioning
5. **Web API** - Enable programmatic access

## Settings Categories

### 1. General Settings

Basic application behavior:
- Language preferences
- Startup options
- Update preferences

### 2. LLM Settings

AI model configuration:
- Provider selection
- Model choice
- Temperature adjustment
- API key storage

### 3. UI Settings

Visual customization:
- Theme selection
- Opacity control
- Font settings
- Layout options

### 4. Hotkey Settings

Keyboard shortcut configuration:
- View all hotkeys
- Customize combinations
- Platform defaults
- Conflict detection

### 5. Prompt Settings

AI prompt customization:
- Edit templates
- Add custom variables
- Save variations
- Reset to defaults

### 6. Web Server Settings

API server configuration:
- Enable/disable server
- Port configuration
- Auto-start option
- Network settings

## Configuration File

Settings are stored in JSON format in the data directory:

**Location:**
- macOS: `~/.interview_corvus/settings.json`
- Windows: `%USERPROFILE%\.interview_corvus\settings.json`
- Linux: `~/.interview_corvus/settings.json`

### Manual Editing

You can manually edit the configuration file:

```json
{
  "api_provider": "openai",
  "model": "gpt-4o",
  "temperature": 0.7,
  "default_language": "Python",
  "theme": "dark",
  "window_opacity": 0.95,
  "always_on_top": true,
  "web_server_autostart": false,
  "web_server_port": 8000
}
```

:::caution
Always backup the settings file before manual editing. Invalid JSON will reset to defaults.
:::

## Import/Export Settings

### Exporting Settings

Share your configuration or backup:

1. Open settings
2. Click **Export Settings**
3. Choose save location
4. Settings saved as `.json` file

### Importing Settings

Apply settings from another machine:

1. Open settings
2. Click **Import Settings**
3. Select settings file
4. Confirm import
5. Restart application

## Profiles (Future Feature)

*Coming soon:* Support for multiple configuration profiles for different use cases:
- Interview prep profile
- Learning profile
- API-only profile
- Quick reference profile

## Resetting to Defaults

### Reset All Settings

To restore factory defaults:

1. Open settings
2. Navigate to **Advanced** tab
3. Click **Reset All Settings**
4. Confirm action
5. Application will restart

### Reset Specific Settings

Reset individual categories:
- **Hotkeys** - Reset to platform defaults
- **Prompts** - Restore original templates
- **UI** - Return to default theme/layout
- **LLM** - Clear API keys and model settings

## Settings Sync (Future Feature)

*Planned:* Sync settings across devices:
- Cloud backup
- Multi-device sync
- Team settings sharing
- Version control

## Best Practices

### Security

- **Never share** your API keys
- **Encrypt backups** containing API keys
- **Rotate keys** periodically
- **Use environment variables** for API keys in automation

### Performance

- **Adjust temperature** based on problem complexity
- **Choose appropriate models** (speed vs quality)
- **Clear history** regularly
- **Optimize hotkeys** for your workflow

### Workflow

- **Customize hotkeys** to avoid conflicts
- **Set default language** to your most-used
- **Configure opacity** for your monitor setup
- **Enable auto-start** if using daily

## Troubleshooting

### Settings Not Saving

- Check file permissions on settings directory
- Ensure disk space available
- Verify JSON syntax if manually edited
- Try running as administrator (Windows)

### Hotkey Conflicts

- Check system-wide hotkeys
- Avoid common shortcuts
- Use platform-specific guidelines
- Test each hotkey after setting

### API Keys Not Persisting

- Grant Keychain access (macOS)
- Run as administrator (Windows)
- Check security software interference
- Verify keyring library installation

## Next Steps

Explore specific customization topics:

- [Hotkey Configuration](./hotkeys.md) - Customize all keyboard shortcuts
- [Advanced Features](../usage/advanced-features.md) - Learn advanced usage patterns
