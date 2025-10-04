# Interview Corvus

An AI-powered invisible assistant designed specifically for technical coding interviews. Named after the corvid family of birds known for their exceptional intelligence, this application provides real-time coding solutions while remaining invisible during screen sharing sessions.

## Getting Started

### Prerequisites

- Python 3.11 or higher (up to 3.14)
- OpenAI API key (GPT-4 or GPT-4o recommended) or Anthropic API key
- Poetry (for development from source)

### Installation

#### Option 1: Download Release (Recommended)
1. Visit the [Releases](https://github.com/sumansaurabh/acebot/releases) page
2. Download the appropriate version for your platform (macOS .dmg or Windows .zip)
3. Install and grant necessary permissions (Screen Recording, Accessibility)

#### Option 2: Build from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/sumansaurabh/acebot.git
   cd acebot
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Run the application:
   ```bash
   poetry run python interview_corvus/main.py
   ```

## Usage

### Basic Usage
1. Launch Interview Corvus
2. Enter your API key in the settings
3. Take a screenshot of a coding problem using the hotkey
4. Generate a solution with another hotkey
5. Use the "Hide" button to make the app invisible when needed

### Default Hotkeys
| Function | macOS | Windows |
|----------|-------|---------|
| Take Screenshot | Cmd+Ctrl+1 | Ctrl+Alt+1 |
| Generate Solution | Cmd+Ctrl+2 | Ctrl+Alt+2 |
| Toggle Visibility | Cmd+Ctrl+B | Ctrl+Alt+B |

### Web API Usage
```bash
# Start the web server from GUI or run standalone
python api_server.py

# Upload image and get solution
curl -X POST "http://127.0.0.1:8000/upload-solution" \
     -F "files=@problem.png" \
     -F "language=Python"
```

## Features

- **Invisible during screen sharing** - Hide the app instantly with hotkeys
- **AI-powered coding solutions** - Get complete solutions with detailed explanations
- **Time & space complexity analysis** - Understand the efficiency of your algorithms
- **Screenshot problem solving** - Capture coding problems directly from your screen
- **Multi-language support** - Python, Java, JavaScript, C++, C#, Go, Rust, Ruby
- **Edge case handling** - Identify and address potential edge cases in your solutions
- **Web API** - Built-in REST API for integration with other tools
- **Global hotkey controls** - Use the app even when it's not in focus

## Contributing

1. Fork the project
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

**Author**: npavlin - afaneor@gmail.com

**Project Link**: [https://github.com/sumansaurabh/acebot](https://github.com/sumansaurabh/acebot)

**API Documentation**: Visit `http://127.0.0.1:8000/docs` when running the web server
