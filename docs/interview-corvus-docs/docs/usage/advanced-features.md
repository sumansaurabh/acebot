---
sidebar_position: 2
---

# Advanced Features

Explore the advanced features of Interview Corvus to maximize your interview preparation.

## Multi-Screenshot Analysis

Interview Corvus can analyze multiple screenshots at once, useful for:
- Problems with multiple parts
- Long problem statements
- Problems with visual diagrams
- Reference materials

### How to Use

1. Take first screenshot: `Cmd+Ctrl+1` (macOS) or `Ctrl+Alt+1` (Windows)
2. Take additional screenshots: Repeat the hotkey
3. Generate solution: `Cmd+Ctrl+2` (macOS) or `Ctrl+Alt+2` (Windows)

The AI will analyze all screenshots together for comprehensive understanding.

## Custom Prompt Templates

Customize how the AI generates solutions by modifying prompt templates in Settings.

### Available Templates

**Code Solution Prompt**
- Controls initial solution generation
- Customize output format
- Adjust verbosity level

**Optimization Prompt**
- Defines optimization strategies
- Focus areas (speed, memory, readability)
- Alternative approaches

**Complexity Analysis Prompt**
- How complexity is analyzed
- Level of detail
- Explanation style

**Screenshot Solution Prompt**
- OCR and visual analysis parameters
- Problem extraction strategy
- Image processing preferences

### Editing Templates

1. Open **Settings → Prompts**
2. Select the template to modify
3. Edit the prompt text
4. Save changes
5. Test with a new problem

### Template Variables

Use these variables in your prompts:

- `{language}` - Selected programming language
- `{problem}` - Extracted problem text
- `{code}` - Current code (for optimization)
- `{constraints}` - Problem constraints

## LLM Model Selection

### Supported Providers

**OpenAI**
- GPT-4o (recommended)
- GPT-4 Turbo
- o3-mini

**Anthropic**
- Claude 3.5 Sonnet (recommended)
- Claude 3 Opus
- Claude 3 Haiku

### Model Configuration

In Settings → LLM:

1. **API Provider** - Choose OpenAI or Anthropic
2. **Model** - Select specific model
3. **Temperature** - Adjust creativity (0.0-2.0)
   - Lower (0.0-0.3): More deterministic, consistent
   - Medium (0.4-0.7): Balanced
   - Higher (0.8-2.0): More creative, varied

### When to Change Models

**Use faster models (Haiku, GPT-3.5) when:**
- Simple problems
- Quick explanations needed
- Cost is a concern
- Testing functionality

**Use advanced models (Sonnet, GPT-4o) when:**
- Complex algorithms
- Detailed explanations needed
- Multiple optimization passes
- Interview preparation

## Session Persistence

Interview Corvus maintains context across your session.

### What's Saved

- Screenshot history
- Generated solutions
- Chat context
- Optimization attempts

### Benefits

- Build on previous solutions
- Compare different approaches
- Reference earlier explanations
- Maintain conversation flow

### Clearing Sessions

Reset when:
- Starting a new problem type
- Context becomes too large
- Want fresh analysis
- After completing a problem

Use `Cmd+Ctrl+R` (macOS) or `Ctrl+Alt+R` (Windows)

## Panic Mode

Instantly hide the application in emergency situations.

### Activation

**Fastest Hide:**
- **macOS**: `Cmd+Q`
- **Windows**: `Alt+Q`

### What Happens

1. Window disappears immediately
2. No animation or delay
3. Process continues running
4. Quick restore available

### Restoring

- **macOS**: Click app icon in Dock
- **Windows**: Click taskbar icon or system tray

## Code Optimization Workflow

### Multi-Pass Optimization

Generate multiple optimization levels:

```
Initial Solution → Optimize → Optimize Again → Compare
```

Each pass can focus on:
- Time complexity improvements
- Space complexity reduction
- Code readability
- Different algorithms

### Comparing Solutions

Keep track of:
- Original complexity
- Optimized complexity
- Trade-offs made
- Performance gains

### Implementation Strategies

1. **Start Simple** - Get working solution first
2. **Optimize Gradually** - One improvement at a time
3. **Test Each Version** - Verify correctness
4. **Document Changes** - Note what changed and why

## Language-Specific Features

### Python

- PEP 8 style compliance
- Type hints when appropriate
- Pythonic idioms
- Built-in function usage

### JavaScript

- Modern ES6+ syntax
- Functional programming patterns
- Array method chains
- Async/await patterns

### Java

- Object-oriented best practices
- Stream API usage
- Generic types
- Exception handling

### C++

- STL containers and algorithms
- Modern C++11/14/17 features
- Memory management
- Performance optimizations

## Web API Integration

Use Interview Corvus programmatically through the Web API.

### Starting the Server

**From GUI:**
1. Click "Start Web Server" button
2. Or enable "Start on Launch" in settings

**Standalone:**
```bash
poetry run python api_server.py
```

### Basic Usage

```bash
# Health check
curl http://127.0.0.1:8000/health

# Upload and solve
curl -X POST "http://127.0.0.1:8000/upload-solution" \
     -F "files=@problem.png" \
     -F "language=Python"
```

See the [Web API Documentation](../api/overview.md) for complete reference.

## Batch Processing

Process multiple problems efficiently:

1. **Prepare Problems** - Collect screenshots or problem descriptions
2. **Configure Language** - Set default in settings
3. **Process Sequentially**:
   - Load problem 1
   - Generate solution
   - Save/review
   - Reset history
   - Repeat for next problem

### Using Web API for Batch

```python
import requests
import os

problems = ['problem1.png', 'problem2.png', 'problem3.png']
language = 'Python'

for problem_file in problems:
    with open(problem_file, 'rb') as f:
        response = requests.post(
            'http://127.0.0.1:8000/upload-solution',
            files={'files': (problem_file, f)},
            data={'language': language}
        )
        solution = response.json()
        # Save or process solution
```

## Keyboard-Only Workflow

For maximum efficiency, use Interview Corvus entirely with keyboard:

1. **Capture**: Screenshot hotkey
2. **Generate**: Solution hotkey
3. **Read**: Scroll with arrow keys
4. **Optimize**: Optimization hotkey
5. **Hide**: Visibility toggle hotkey
6. **Reset**: Clear history hotkey
7. **Move**: Window position hotkeys

No mouse required!

## Best Practices

### For Interview Prep

1. **Practice Timing** - Simulate real interview conditions
2. **Limit Usage** - Don't become dependent
3. **Understand First** - Read solution before copying
4. **Modify Solutions** - Adapt to your style
5. **Test Thoroughly** - Always verify correctness

### For Learning

1. **Study Patterns** - Recognize common algorithms
2. **Compare Approaches** - Try multiple solutions
3. **Read Explanations** - Don't skip complexity analysis
4. **Build Intuition** - Understand why solutions work
5. **Practice Variations** - Modify problems slightly

### For Performance

1. **Clear History** - When context gets large
2. **Use Appropriate Models** - Match model to problem complexity
3. **Optimize Screenshots** - Clear, focused captures
4. **Keyboard Shortcuts** - Faster than mouse navigation

## Troubleshooting Advanced Features

### Solutions Not Optimal

- Try optimization feature
- Adjust temperature setting
- Use more advanced model
- Provide more context in screenshot

### API Key Rate Limits

- Use cheaper models for simple problems
- Clear history to reduce token usage
- Space out requests
- Consider API plan upgrade

### Screenshot Recognition Issues

- Ensure good lighting/contrast
- Capture full problem statement
- Avoid compressed/low-quality images
- Include all relevant constraints

## Next Steps

- Customize your [Hotkeys](../customization/hotkeys.md)
- Explore the [Web API](../api/overview.md)
