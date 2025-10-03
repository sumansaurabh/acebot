---
sidebar_position: 4
---

# Hotkey Configuration

Interview Corvus provides extensive hotkey customization to fit your workflow and avoid conflicts with other applications.

## Default Hotkeys

### macOS Default Hotkeys

| Function | Hotkey | Description |
|----------|--------|-------------|
| **Take Screenshot** | `Cmd+Ctrl+1` | Capture coding problem from screen |
| **Generate Solution** | `Cmd+Ctrl+2` | Generate AI-powered solution |
| **Toggle Visibility** | `Cmd+Ctrl+B` | Hide/show application |
| **Optimize Solution** | `Cmd+Ctrl+O` | Improve existing solution |
| **Reset History** | `Cmd+Ctrl+R` | Clear all solutions |
| **Panic Hide** | `Cmd+Q` | Instantly hide application |
| **Move Window Up** | `Cmd+Up` | Move window to upper screen area |
| **Move Window Down** | `Cmd+Down` | Move window to lower screen area |
| **Move Window Left** | `Cmd+Left` | Move window to left screen area |
| **Move Window Right** | `Cmd+Right` | Move window to right screen area |

### Windows Default Hotkeys

| Function | Hotkey | Description |
|----------|--------|-------------|
| **Take Screenshot** | `Ctrl+Alt+1` | Capture coding problem from screen |
| **Generate Solution** | `Ctrl+Alt+2` | Generate AI-powered solution |
| **Toggle Visibility** | `Ctrl+Alt+B` | Hide/show application |
| **Optimize Solution** | `Ctrl+Alt+O` | Improve existing solution |
| **Reset History** | `Ctrl+Alt+R` | Clear all solutions |
| **Panic Hide** | `Alt+Q` | Instantly hide application |
| **Move Window Up** | `Win+Up` | Move window to upper screen area |
| **Move Window Down** | `Win+Down` | Move window to lower screen area |
| **Move Window Left** | `Win+Left` | Move window to left screen area |
| **Move Window Right** | `Win+Right` | Move window to right screen area |

> **Note**: The "Win" key refers to the Windows key (⊞) on your keyboard.

## Customizing Hotkeys

### Step-by-Step Customization

1. **Open Settings**
   - Click the "Settings" button in the main interface
   - Or use the menu: File → Settings

2. **Navigate to Hotkeys Tab**
   - Click on the "Hotkeys" tab in the settings window

3. **Modify Hotkeys**
   - Click on any hotkey field
   - Press your desired key combination
   - The new hotkey will be automatically detected

4. **Save Changes**
   - Press "OK" to save your custom hotkeys
   - Changes take effect immediately

### Hotkey Guidelines

**Recommended Patterns:**
- Use modifier keys (Ctrl, Alt, Cmd, Win) for global hotkeys
- Avoid single-key hotkeys that might conflict with typing
- Consider using function keys (F1-F12) for less common actions
- Test combinations to ensure they don't conflict with other apps

**Common Modifier Combinations:**
- `Ctrl+Alt+[Key]` - Good for Windows
- `Cmd+Ctrl+[Key]` - Good for macOS
- `Shift+Alt+[Key]` - Alternative option
- `Win+[Key]` - Windows-specific (use carefully)

### Resetting Hotkeys

**Reset All to Defaults:**
1. Open the Hotkeys settings tab
2. Click "Reset All Hotkeys to Defaults"
3. Confirm the action
4. All hotkeys return to platform-specific defaults

**Reset Individual Hotkeys:**
- Right-click on a hotkey field
- Select "Reset to Default" (if available)
- Or manually enter the default combination

## Platform-Specific Considerations

### macOS Considerations

**System Integration:**
- macOS may require you to grant Accessibility permissions
- Some combinations might conflict with system shortcuts
- Test hotkeys with Mission Control and Spotlight

**Common Conflicts:**
- `Cmd+Space`: Spotlight Search
- `Cmd+Tab`: Application Switcher
- `Cmd+Shift+3/4`: System Screenshots

**Solutions:**
- Use `Ctrl` instead of `Cmd` for some combinations
- Add additional modifiers (e.g., `Cmd+Ctrl+Shift+1`)
- Choose function keys for less common actions

### Windows Considerations

**System Integration:**
- May require administrator privileges for global hotkeys
- Windows 10/11 shortcuts might conflict
- Test with Windows key combinations carefully

**Common Conflicts:**
- `Win+D`: Show Desktop
- `Win+L`: Lock Screen
- `Ctrl+Alt+Del`: Security Screen

**Solutions:**
- Use `Ctrl+Shift` combinations
- Avoid Windows key for critical functions
- Use less common key combinations

## Advanced Configuration

### Global vs. Local Hotkeys

**Global Hotkeys:**
- Work when Interview Corvus is not focused
- Essential for stealth operation during interviews
- Require special system permissions

**Local Hotkeys:**
- Only work when the application has focus
- Safer but less convenient
- Good fallback option

### Context-Aware Hotkeys

Some hotkeys are context-sensitive:
- **Screenshot hotkey**: Only works when no screenshot is being processed
- **Solution hotkey**: Requires a screenshot to be available
- **Optimize hotkey**: Only works when a solution exists

### Custom Workflows

**Example Custom Setup:**
```
F1 - Take Screenshot
F2 - Generate Solution
F3 - Optimize Solution
F4 - Toggle Visibility
F5 - Reset History
```

**Advantages:**
- No conflicts with system shortcuts
- Easy to remember sequential pattern
- Works across all platforms

## Troubleshooting Hotkeys

### Common Issues

**Hotkeys Not Working:**
1. Check if permissions are granted (Accessibility on macOS)
2. Verify no other application is using the same combination
3. Try running as administrator (Windows)
4. Test with simpler key combinations

**Conflicts with Other Applications:**
1. Identify the conflicting application
2. Either change Interview Corvus hotkeys or the other app
3. Use more specific modifier combinations
4. Consider using function keys

**Partial Functionality:**
- Some hotkeys work, others don't
- Usually indicates permission or conflict issues
- Try resetting to defaults and reconfiguring

### Best Practices

**For Interviews:**
1. **Test all hotkeys** before the interview
2. **Have backup combinations** ready
3. **Practice** the key sequences until they're muscle memory
4. **Keep a cheat sheet** nearby (hidden from camera)

**For Daily Use:**
1. **Choose memorable patterns** (e.g., Ctrl+Alt+1,2,3...)
2. **Avoid** combinations you use frequently in other apps
3. **Document** your custom setup
4. **Regular testing** to ensure they still work

## Next Steps

Now that you've configured your hotkeys:
- [Usage Guide](/docs/usage) - Learn effective workflows
- [Best Practices](/docs/best-practices) - Interview tips and strategies
- [API Configuration](/docs/api-configuration) - Optimize AI responses