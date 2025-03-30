# Interview Corvus

> **Created by [Nikolay Pavlin](https://t.me/pavlin_share)** - Follow my Telegram channel for updates, tips, and more useful tools!
> 
> Support this project: [Boosty](https://boosty.to/nikolay-pavlin/donate) | TRC20: `TE685e5rWAebT2JSCpcLW9UEVCfGLGaqRN`

![example](img/example.png)

Interview Corvus is an AI-powered invisible assistant designed specifically for technical coding interviews. Named after the corvid family of birds (crows, ravens) known for their exceptional intelligence, this application offers real-time coding solutions while remaining invisible during screen sharing sessions.

This open-source project was inspired by [interview-coder](https://github.com/ibttf/interview-coder) and extends the functionality with advanced features like screenshot analysis, multi-language support, and customizable AI prompts.

## Key Features

- **Invisible during screen sharing** - Hide the app instantly with hotkeys
- **AI-powered coding solutions** - Get complete solutions with detailed explanations
- **Time & space complexity analysis** - Understand the efficiency of your algorithms
- **Screenshot problem solving** - Capture coding problems directly from your screen
- **Multi-language support** - Python, Java, JavaScript, C++, C#, Go, Rust, Ruby
- **Edge case handling** - Identify and address potential edge cases in your solutions
- **Optimization suggestions** - Improve your initial solutions with one click
- **Global hotkey controls** - Use the app even when it's not in focus

## Installation

### Prerequisites

- OpenAI API key (GPT-4 or GPT-4o recommended) or Anthropic API key
- Python 3.11+ (if running from source)

### Download

You can get the latest version by:

1. Downloading the release for your platform from the [Releases](https://github.com/afaneor/interview-corvus/releases) page (currently available only for macos)
2. Or building/using from source using the instructions below

### Building from Source

```bash
# Clone the repository
git clone https://github.com/your-username/interview-corvus.git
cd interview-corvus

# Install dependencies
poetry install

# Run the application
poetry run python interview_corvus/main.py

# Build for your platform
poetry run python build.py
```

## Customization Options
**(default settings are store in interview_corvus/config.py)**

### LLM Settings

- **API Provider** - Choose between OpenAI and Anthropic
- **Model Selection** - Select from GPT-4o, GPT-4-turbo, GPT-3.5-turbo, or Claude models
- **Temperature** - Adjust creativity vs. determinism of responses (0.0-2.0)
- **API Key Management** - Securely store your API keys

### UI Customization

- **Theme** - Choose between Light and Dark themes
- **Window Opacity** - Adjust transparency for better integration with your workspace
- **Always On Top** - Keep the window visible on top of other applications
- **Default Language** - Set your preferred programming language

### Prompt Templates

All prompt templates can be customized to your preference:
- **Code Solution** - Customize how solutions are generated
- **Code Optimization** - Modify optimization strategies
- **Complexity Analysis** - Adjust how time and space complexity are analyzed
- **Screenshot Solution** - Configure OCR and visual analysis parameters

## Usage Guide

1. Launch Interview Corvus
2. Enter your API key in the settings
3. Take a screenshot of a coding problem using the hotkey (Cmd+Ctrl+1 on macOS by default)
4. Generate a solution with another hotkey (Cmd+Ctrl+2 on macOS by default)
5. Use the "Hide" button or hotkey (Cmd+Ctrl+B) to make the app invisible when needed

### Keyboard Shortcuts

| Function | macOS | Windows/Linux |
|----------|-------|---------------|
| Take Screenshot | Cmd+Ctrl+1 | Ctrl+Alt+1 |
| Generate Solution | Cmd+Ctrl+2 | Ctrl+Alt+2 |
| Toggle Visibility | Cmd+Ctrl+B | Ctrl+Alt+B |
| Move Window Up | Cmd+Up | Ctrl+Up |
| Move Window Down | Cmd+Down | Ctrl+Down |
| Move Window Left | Cmd+Left | Ctrl+Left |
| Move Window Right | Cmd+Right | Ctrl+Right |
| Optimize Solution | Cmd+Ctrl+O | Ctrl+Alt+O |
| Reset History | Cmd+Ctrl+R | Ctrl+Alt+R |
| Panic (Instantly Hide) | Cmd+Q | Alt+Q |

## Required Permissions

### macOS
When using Interview Corvus on macOS, you'll need to grant the following permissions:

- **Screen Recording** - Required for taking screenshots of coding problems
- **Accessibility** - Required for global hotkeys when the app is not in focus
- **Keychain Access** - Used by the keyring library to securely store your API key

To grant these permissions, follow the prompts or go to System Preferences → Security & Privacy → Privacy tab.

### Windows
On Windows, you may need to run as administrator to enable some features.

## Data Storage

By default, Interview Corvus stores its data in the following locations:

- macOS: `~/.interview_corvus/`
- Windows: `%USERPROFILE%\.interview_corvus\`
- Linux: `~/.interview_corvus/`

This includes screenshots, user settings, and other application data.

## Best Practices for Technical Interviews

Interview Corvus works best when you:

1. Take a clear screenshot of the entire problem including constraints
2. Select the appropriate programming language for your interview
3. Use the "Optimize Solution" feature after generating the initial solution
4. Study the provided time and space complexity analysis
5. Hide the app before sharing your screen for the actual interview

## Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request
# interview-corvus
