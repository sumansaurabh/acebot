# Interview Corvus

An AI-powered assistant for technical coding interviews that remains invisible during screen sharing.

## Quick Start

1. Download the latest release for your platform
2. Install and run the application
3. Add your OpenAI or Anthropic API key in settings
4. Use hotkeys to capture problems and generate solutions

## Key Features

- Invisible during screen sharing
- AI-powered coding solutions
- Screenshot problem analysis
- Multi-language support (Python, Java, JavaScript, C++, C#, Go, Rust, Ruby)
- Time & space complexity analysis
- Global hotkey controls

## Installation

### macOS
Download the `.dmg` file, drag to Applications, and grant required permissions (Screen Recording, Accessibility).

### Windows
Download the `.zip` file, extract, and run `Interview Corvus.exe`.

### From Source
```bash
git clone https://github.com/your-username/interview-corvus.git
cd interview-corvus
poetry install
poetry run python interview_corvus/main.py
```

## Default Hotkeys

| Function | macOS | Windows |
|----------|-------|---------|
| Take Screenshot | Cmd+Ctrl+1 | Ctrl+Alt+1 |
| Generate Solution | Cmd+Ctrl+2 | Ctrl+Alt+2 |
| Toggle Visibility | Cmd+Ctrl+B | Ctrl+Alt+B |
| Panic Hide | Cmd+Q | Alt+Q |

All hotkeys are customizable in Settings.

## Credits

Created by [Nikolay Pavlin](https://t.me/pavlin_share)

Inspired by [interview-coder](https://github.com/ibttf/interview-coder)
