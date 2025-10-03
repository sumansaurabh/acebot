---
sidebar_position: 2
---

# Hotkey Configuration

Customize keyboard shortcuts in Interview Corvus to match your workflow and avoid conflicts with other applications.

## Accessing Hotkey Settings

1. Open **Settings** (Settings button or File → Settings)
2. Navigate to the **Hotkeys** tab
3. Click on any hotkey field to change it
4. Press your desired key combination
5. Click **OK** to save changes

## Default Hotkeys

### macOS Defaults

| Function | Hotkey |
|----------|--------|
| Take Screenshot | `Cmd+Ctrl+1` |
| Generate Solution | `Cmd+Ctrl+2` |
| Toggle Visibility | `Cmd+Ctrl+B` |
| Move Window Up | `Cmd+Up` |
| Move Window Down | `Cmd+Down` |
| Move Window Left | `Cmd+Left` |
| Move Window Right | `Cmd+Right` |
| Optimize Solution | `Cmd+Ctrl+O` |
| Reset History | `Cmd+Ctrl+R` |
| Panic Hide | `Cmd+Q` |

### Windows Defaults

| Function | Hotkey |
|----------|--------|
| Take Screenshot | `Ctrl+Alt+1` |
| Generate Solution | `Ctrl+Alt+2` |
| Toggle Visibility | `Ctrl+Alt+B` |
| Move Window Up | `Win+Up` |
| Move Window Down | `Win+Down` |
| Move Window Left | `Win+Left` |
| Move Window Right | `Win+Right` |
| Optimize Solution | `Ctrl+Alt+O` |
| Reset History | `Ctrl+Alt+R` |
| Panic Hide | `Alt+Q` |

:::info
On Linux systems, the "Win" key is often called the "Super" key.
:::

## Customizing Hotkeys

### Creating Custom Combinations

When setting a hotkey:

1. **Click the hotkey field**
2. **Press your desired combination** (e.g., `Ctrl+Shift+S`)
3. **The field updates immediately**
4. **Save settings** when done

### Valid Key Combinations

You can use:
- **Modifiers**: Ctrl, Alt, Shift, Cmd/Win
- **Letters**: A-Z
- **Numbers**: 0-9
- **Function Keys**: F1-F12
- **Special Keys**: Up, Down, Left, Right, Space, etc.

### Best Practices

✅ **Do:**
- Use multiple modifiers (e.g., `Ctrl+Shift+Key`)
- Choose memorable combinations
- Test each hotkey after setting
- Avoid system shortcuts

❌ **Don't:**
- Use single keys without modifiers
- Conflict with system shortcuts
- Use common application shortcuts
- Make combinations too complex

## Common Hotkey Conflicts

### macOS

Avoid conflicts with:
- **Cmd+Q** - Quit application (our panic hide uses this intentionally)
- **Cmd+W** - Close window
- **Cmd+Tab** - Application switcher
- **Cmd+Space** - Spotlight
- **Cmd+C/V** - Copy/Paste

### Windows

Avoid conflicts with:
- **Win+L** - Lock screen
- **Win+D** - Show desktop
- **Ctrl+Alt+Del** - Task manager
- **Alt+Tab** - Window switcher
- **Ctrl+C/V** - Copy/Paste

### Application-Specific

If you use these tools, avoid their hotkeys:
- **IDEs** - VSCode, IntelliJ, PyCharm
- **Browsers** - Chrome, Firefox shortcuts
- **Screen Capture** - Built-in screenshot tools
- **Window Managers** - Rectangle, BetterSnapTool

## Hotkey Function Reference

### Screenshot Functions

**Take Screenshot**
- Captures a region of the screen
- Automatically analyzes the content
- Can be used multiple times
- Default: `Cmd+Ctrl+1` (macOS), `Ctrl+Alt+1` (Windows)

### Solution Functions

**Generate Solution**
- Processes captured screenshots
- Generates code solution
- Provides complexity analysis
- Default: `Cmd+Ctrl+2` (macOS), `Ctrl+Alt+2` (Windows)

**Optimize Solution**
- Improves current solution
- Suggests better algorithms
- Analyzes trade-offs
- Default: `Cmd+Ctrl+O` (macOS), `Ctrl+Alt+O` (Windows)

### Visibility Functions

**Toggle Visibility**
- Shows/hides window
- Maintains app state
- Smooth transition
- Default: `Cmd+Ctrl+B` (macOS), `Ctrl+Alt+B` (Windows)

**Panic Hide**
- Instant hide, no animation
- Emergency use only
- Quick restore available
- Default: `Cmd+Q` (macOS), `Alt+Q` (Windows)

### Window Management

**Move Window Up/Down/Left/Right**
- Repositions window on screen
- Useful for multi-monitor setups
- Consistent movement increments
- Default: `Cmd+Arrow` (macOS), `Win+Arrow` (Windows)

### History Management

**Reset History**
- Clears all screenshots
- Resets chat context
- Starts fresh session
- Default: `Cmd+Ctrl+R` (macOS), `Ctrl+Alt+R` (Windows)

## Platform-Specific Considerations

### macOS

**Command Key Usage**
- Primary modifier is `Cmd` not `Ctrl`
- `Ctrl` is available for combinations
- Function keys may require `Fn`

**Accessibility Required**
- Global hotkeys need Accessibility permission
- Grant in System Preferences → Security & Privacy
- Application must be in the list

**Keyboard Layout**
- Works with all keyboard layouts
- International keyboards supported
- Special characters may vary

### Windows

**Windows Key Usage**
- Windows key available for combinations
- Some combinations reserved by system
- May need admin rights

**Function Keys**
- F1-F12 available
- May conflict with laptop special functions
- Check OEM keyboard software

**Keyboard Layout**
- Supports all Windows keyboard layouts
- International layouts compatible
- Test after changing layouts

### Linux

**Super Key**
- Windows/Super key available
- Desktop environment may reserve some combinations
- Check DE-specific shortcuts

**Window Managers**
- i3, Awesome, etc. have their own hotkeys
- Coordinate with WM configuration
- May need to disable conflicting bindings

## Troubleshooting Hotkeys

### Hotkeys Not Working

**Check permissions:**
- macOS: Accessibility permission granted
- Windows: Run as administrator if needed
- Linux: Input device access

**Test conflicts:**
- Disable other apps temporarily
- Try different key combination
- Check system-wide shortcuts

**Verify settings:**
- Hotkeys saved correctly
- Application restarted after changes
- No duplicate assignments

### Hotkeys Triggering Wrong Action

**Clear cache:**
1. Close application
2. Delete settings cache
3. Restart application
4. Reconfigure hotkeys

**Reset hotkeys:**
1. Open Settings → Hotkeys
2. Click "Reset All Hotkeys to Defaults"
3. Customize again

### Global Hotkeys Not Global

**Permission issues:**
- Grant Accessibility access (macOS)
- Run as administrator (Windows)
- Check input group membership (Linux)

**Application focus:**
- Some hotkeys work only when focused
- Global hotkeys should work anytime
- Verify in hotkey settings

## Advanced Hotkey Tips

### Workflow Optimization

Group related functions:
- **Screenshot + Solution**: Use sequential numbers (`1`, `2`)
- **Visibility controls**: Use same base + different modifier
- **Window management**: Use arrow keys with modifier

### Ergonomic Considerations

- **Frequently used**: Easy to reach (e.g., `Ctrl+Shift+S`)
- **Rarely used**: Can be more complex (e.g., `Ctrl+Shift+Alt+R`)
- **Emergency (Panic)**: Quick single action (e.g., `Alt+Q`)

### Multi-Monitor Setup

For multiple monitors:
- Use window movement hotkeys frequently
- Position window on secondary monitor
- Keep interviewer's view on primary

### One-Handed Operation

Design hotkeys for one hand:
- Left hand: `Ctrl+Shift+A/S/D/F`
- Right hand: `Ctrl+Shift+J/K/L/;`
- Useful when using mouse with other hand

## Exporting/Importing Hotkey Configurations

### Export Hotkeys

Save your hotkey configuration:

1. Open Settings → Advanced
2. Click "Export Settings"
3. Include hotkeys in export
4. Save to file

### Import Hotkeys

Apply saved configuration:

1. Open Settings → Advanced
2. Click "Import Settings"
3. Select settings file
4. Hotkeys applied automatically

### Sharing Configurations

Share with team:
- Export to file
- Share via email/chat
- Others import to use same hotkeys
- Useful for pair programming

## Keyboard Layouts and International Support

### Non-US Keyboards

- QWERTY layouts fully supported
- AZERTY layouts work
- QWERTZ layouts compatible
- Test your specific layout

### Special Characters

Some layouts may have:
- Different positions for brackets
- Alternate number row access
- Modified symbol keys

**Recommendation**: Use letters and standard modifiers for consistency.

## Resetting Hotkeys

### Reset All to Defaults

1. Open Settings → Hotkeys
2. Click "Reset All Hotkeys to Defaults"
3. Confirm action
4. Platform-specific defaults applied

### Reset Individual Hotkey

1. Click hotkey field
2. Press `Backspace` or `Delete`
3. Field clears
4. Assign new combination or leave empty

## Best Hotkey Setups

### For Beginners

Keep it simple:
- Screenshot: `Ctrl+Shift+1`
- Solution: `Ctrl+Shift+2`
- Hide: `Ctrl+Shift+H`

### For Power Users

Optimized workflow:
- Screenshot: `Ctrl+Alt+S`
- Solution: `Ctrl+Alt+G`
- Optimize: `Ctrl+Alt+O`
- Hide: `Ctrl+Alt+H`
- Panic: `Alt+Esc`

### For Interviews

Quick access:
- Screenshot: `F1`
- Solution: `F2`
- Optimize: `F3`
- Panic Hide: `F12`

## Next Steps

- Learn about [Advanced Features](../usage/advanced-features.md)
- Explore the [Web API](../api/overview.md)
