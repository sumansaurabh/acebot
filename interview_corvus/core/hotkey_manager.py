from loguru import logger
from pynput import keyboard
from PyQt6.QtCore import QEvent, QObject, pyqtBoundSignal, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut

from interview_corvus.config import settings


class HotkeyManager(QObject):
    """
    Manager for registering and handling global hotkeys.

    Signals:
        screenshot_triggered: Emitted when the screenshot hotkey is pressed
        solution_triggered: Emitted when the generate solution hotkey is pressed
        visibility_triggered: Emitted when the toggle visibility hotkey is pressed
        move_window_triggered: Emitted with direction when a move window hotkey is pressed
        panic_triggered: Emitted when the panic hotkey is pressed
        reset_history_triggered: Emitted when the reset history hotkey is pressed
        optimize_solution_triggered: Emitted when the optimize solution hotkey is pressed
    """

    screenshot_triggered = pyqtSignal()
    solution_triggered = pyqtSignal()
    visibility_triggered = pyqtSignal()
    move_window_triggered = pyqtSignal(str)
    panic_triggered = pyqtSignal()
    reset_history_triggered = pyqtSignal()
    optimize_solution_triggered = pyqtSignal()

    def __init__(self):
        """Initialize the hotkey manager."""
        super().__init__()

        # Initialize key mappings based on config
        self.hotkeys = {
            settings.hotkeys.screenshot_key: self.screenshot_triggered,
            settings.hotkeys.generate_solution_key: self.solution_triggered,
            settings.hotkeys.toggle_visibility_key: self.visibility_triggered,
            settings.hotkeys.panic_key: self.panic_triggered,
            settings.hotkeys.reset_history_key: self.reset_history_triggered,
            settings.hotkeys.optimize_solution_key: self.optimize_solution_triggered,
        }

        # Add move window keys
        for direction, key in settings.hotkeys.move_window_keys.items():
            self.hotkeys[key] = lambda dir=direction: self.move_window_triggered.emit(
                dir
            )

        # List of registered shortcuts to maintain references
        self.shortcuts = []

        # Debug mode
        self.debug = settings.debug_mode
        self.keys_of_interest = set()
        self.current_keys = set()
        self.key_listener = None
        self.pynput_hotkeys = {}
        
        # Check if global hotkeys should be disabled via environment variable
        import os
        disable_global = os.environ.get('DISABLE_GLOBAL_HOTKEYS', '').lower() in ('1', 'true', 'yes')
        self.global_hotkeys_enabled = not disable_global
        
        if disable_global:
            logger.info("Global hotkeys disabled via environment variable DISABLE_GLOBAL_HOTKEYS")
            
        # self._convert_hotkeys_to_pynput_format()

    def __del__(self):
        """Destructor to ensure proper cleanup."""
        self.cleanup()

    def cleanup(self):
        """Clean up resources when the hotkey manager is destroyed."""
        try:
            self.stop_global_listener()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def _convert_hotkeys_to_pynput_format(self):
        """Converts shortcuts from PyQt format to pynput format."""
        for shortcut_str, signal in self.hotkeys.items():
            keys_set = set()

            # Split the shortcut string into individual keys
            parts = shortcut_str.split("+")
            logger.info(f"Converting shortcut: {shortcut_str}, parts: {parts}")

            for part in parts:
                part = part.strip()
                if part.lower() == "ctrl":
                    keys_set.add(keyboard.Key.ctrl)
                elif part.lower() == "cmd":
                    keys_set.add(keyboard.Key.cmd)
                elif part.lower() == "alt":
                    keys_set.add(keyboard.Key.alt)
                elif part.lower() == "shift":
                    keys_set.add(keyboard.Key.shift)
                elif len(part) == 1:
                    # For single character keys, just add lowercase version
                    # We'll handle case sensitivity in the event handlers
                    key_code = keyboard.KeyCode.from_char(part.lower())
                    keys_set.add(key_code)
                    logger.info(
                        f"Added character key: {part.lower()}, KeyCode: {key_code}"
                    )
                else:
                    # Special keys
                    try:
                        if part.lower() == "return":
                            keys_set.add(keyboard.Key.enter)
                        elif part.lower() == "up":
                            keys_set.add(keyboard.Key.up)
                        elif part.lower() == "down":
                            keys_set.add(keyboard.Key.down)
                        elif part.lower() == "left":
                            keys_set.add(keyboard.Key.left)
                        elif part.lower() == "right":
                            keys_set.add(keyboard.Key.right)
                        elif part.lower() == "esc":
                            keys_set.add(keyboard.Key.esc)
                        elif part.lower() == "tab":
                            keys_set.add(keyboard.Key.tab)
                        elif part.lower() == "space":
                            keys_set.add(keyboard.Key.space)
                        # Add other special keys as needed
                    except Exception as e:
                        logger.info(f"Failed to map key: {part}, error: {e}")

            # Store the required keys and associated signal
            hotkey_set = frozenset(keys_set)
            self.pynput_hotkeys[hotkey_set] = signal
            logger.info(
                f"Registered hotkey set: {hotkey_set} for shortcut: {shortcut_str}"
            )

            # Add all keys to the keys_of_interest set
            for key in keys_set:
                self.keys_of_interest.add(key)

        logger.info(
            f"Converted {len(self.pynput_hotkeys)} hotkeys, keys of interest: {self.keys_of_interest}"
        )

    def register_hotkeys(self, window) -> None:
        """
        Register all hotkeys with the application.

        Args:
            window: Main window of the application
        """
        # Clear existing hotkeys and rebuild with current settings
        self.hotkeys = {
            settings.hotkeys.screenshot_key: self.screenshot_triggered,
            settings.hotkeys.generate_solution_key: self.solution_triggered,
            settings.hotkeys.toggle_visibility_key: self.visibility_triggered,
            settings.hotkeys.panic_key: self.panic_triggered,
            settings.hotkeys.reset_history_key: self.reset_history_triggered,
            settings.hotkeys.optimize_solution_key: self.optimize_solution_triggered,
        }

        # Add move window keys
        for direction, key in settings.hotkeys.move_window_keys.items():
            self.hotkeys[key] = lambda dir=direction: self.move_window_triggered.emit(
                dir
            )

        # Register local shortcuts through PyQt
        self.shortcuts.clear()

        for key_sequence, signal in self.hotkeys.items():
            shortcut = QShortcut(QKeySequence(key_sequence), window)

            def create_callback(sig):
                return lambda: sig.emit() if isinstance(sig, pyqtBoundSignal) else sig()

            callback = create_callback(signal)
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)

        logger.info(f"Registered {len(self.shortcuts)} local hotkeys")

        # Reset current keys and keys of interest
        self.current_keys = set()
        self.keys_of_interest = set()
        self.pynput_hotkeys = {}

        # Convert hotkeys to pynput format for global detection
        # self._convert_hotkeys_to_pynput_format()

        # Start global listener
        if self.global_hotkeys_enabled:
            self.start_global_listener()
        else:
            logger.info("Global hotkeys are disabled due to previous errors")

    def start_global_listener(self):
        """Starts listening for global hotkeys using pynput."""
        if not self.global_hotkeys_enabled:
            logger.info("Global hotkeys are disabled")
            return
            
        if self.key_listener is not None and self.key_listener.is_alive():
            logger.info("Global hotkey handler is already running")
            return

        # Check accessibility permissions first
        if not self.check_accessibility_permissions():
            logger.warning("Accessibility permissions not granted. Global hotkeys will not work.")
            logger.info("Please grant accessibility permissions in System Preferences > Security & Privacy > Privacy > Accessibility")
            self.global_hotkeys_enabled = False
            return

        try:
            # Update the set of keys of interest
            for keys_set in self.pynput_hotkeys.keys():
                for key in keys_set:
                    self.keys_of_interest.add(key)

            logger.info("Creating keyboard listener...")
            
            # Start the keyboard listener with error handling
            self.key_listener = keyboard.Listener(
                on_press=self.on_key_press, 
                on_release=self.on_key_release,
                suppress=False  # Don't suppress keys to avoid conflicts
            )
            
            logger.info("Starting keyboard listener...")
            
            # Start the listener in a try-catch to handle permission issues
            self.key_listener.start()
            
            # Give it a moment to start and check if it's alive
            import time
            time.sleep(0.1)
            
            if self.key_listener.is_alive():
                logger.info("Global hotkey handler started successfully")
            else:
                logger.error("Keyboard listener failed to start properly")
                self.key_listener = None
                self.global_hotkeys_enabled = False
            
        except Exception as e:
            logger.error(f"Failed to start global hotkey handler: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.info("Global hotkeys will not be available. You may need to grant accessibility permissions.")
            
            # Disable global hotkeys to prevent future crashes
            self.global_hotkeys_enabled = False
            
            # Clean up if there was an error
            if self.key_listener:
                try:
                    self.key_listener.stop()
                except:
                    pass
                self.key_listener = None

    def stop_global_listener(self):
        """Stops listening for global hotkeys."""
        try:
            if self.key_listener and self.key_listener.is_alive():
                self.key_listener.stop()
                self.key_listener.join(timeout=1.0)  # Wait for clean shutdown
                logger.info("Global hotkey handler stopped")
        except Exception as e:
            logger.error(f"Error stopping global hotkey handler: {e}")
        finally:
            self.key_listener = None
            self.current_keys.clear()  # Clear any tracked keys

    def on_key_press(self, key):
        """Handler for key press events from pynput."""
        try:
            # Debug the incoming key
            logger.info(f"Key pressed: {key}, type: {type(key)}")

            # Normalize modifier keys - map specific variants to base forms
            modifier_map = {
                keyboard.Key.shift_l: keyboard.Key.shift,
                keyboard.Key.shift_r: keyboard.Key.shift,
                keyboard.Key.ctrl_l: keyboard.Key.ctrl,
                keyboard.Key.ctrl_r: keyboard.Key.ctrl,
                keyboard.Key.alt_l: keyboard.Key.alt,
                keyboard.Key.alt_r: keyboard.Key.alt,
                keyboard.Key.cmd_l: keyboard.Key.cmd,
                keyboard.Key.cmd_r: keyboard.Key.cmd,
            }

            # Normalize the key if it's a modifier variant
            if key in modifier_map:
                normalized_key = modifier_map[key]
                self.current_keys.add(normalized_key)
                logger.info(f"Added normalized modifier key: {normalized_key} (from {key})")

            # If it's a regular key we care about
            elif key in self.keys_of_interest:
                self.current_keys.add(key)
                logger.info(f"Added key of interest: {key}")

            # For character keys, match by character value
            elif hasattr(key, "char") and key.char:
                for k in self.keys_of_interest:
                    if hasattr(k, "char") and k.char and k.char.lower() == key.char.lower():
                        self.current_keys.add(k)
                        logger.info(f"Added character key: {k} (matched with {key})")
                        break

            # Log current keys after adding
            logger.info(f"Current keys: {self.current_keys}")

            # Simple hotkey matching - check each registered combination
            for hotkey_set, signal in self.pynput_hotkeys.items():
                # A hotkey matches if all its keys are in current_keys
                all_keys_pressed = True

                for hk in hotkey_set:
                    # For character keys, we need to check case-insensitively
                    if hasattr(hk, "char") and hk.char:
                        found = False
                        for ck in self.current_keys:
                            if (
                                hasattr(ck, "char")
                                and ck.char
                                and ck.char.lower() == hk.char.lower()
                            ):
                                found = True
                                break
                        if not found:
                            all_keys_pressed = False
                            break
                    # For normal keys (including normalized modifiers)
                    elif hk not in self.current_keys:
                        all_keys_pressed = False
                        break

                # If all keys in this hotkey set are pressed, trigger the action
                if all_keys_pressed:
                    logger.info(f"Hotkey matched! Set: {hotkey_set}")
                    try:
                        if isinstance(signal, pyqtBoundSignal):
                            signal.emit()
                        else:
                            signal()  # For lambda function callbacks
                    except Exception as e:
                        logger.error(f"Error triggering signal: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        
        except Exception as e:
            logger.error(f"Error in on_key_press: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def on_key_release(self, key):
        """Handler for key release events from pynput."""
        try:
            logger.info(f"Key released: {key}")

            # For direct matches - this works for most keys
            key_removed = False
            for k in list(
                self.current_keys
            ):  # Make a copy to safely modify during iteration
                if k == key:
                    self.current_keys.remove(k)
                    key_removed = True
                    logger.info(f"Removed key by direct match: {k}")
                    break

            # If no direct match found, try character comparison
            if not key_removed and hasattr(key, "char") and key.char:
                for k in list(self.current_keys):
                    if hasattr(k, "char") and k.char and k.char.lower() == key.char.lower():
                        self.current_keys.remove(k)
                        key_removed = True
                        logger.info(f"Removed key by character match: {k}")
                        break

            # Log remaining keys
            logger.info(f"Current keys after release: {self.current_keys}")
            
        except Exception as e:
            logger.error(f"Error in on_key_release: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Filter application events to detect hotkey combinations (backup method).
        Only for in-window shortcuts and as a fallback mechanism.

        Args:
            obj: The object that received the event
            event: The event that was received

        Returns:
            True if the event was handled, False otherwise
        """
        # For internal use in the application - kept as a backup option
        return super().eventFilter(obj, event)

    def check_accessibility_permissions(self):
        """
        Check if the application has accessibility permissions on macOS.
        Returns True if permissions are granted or not on macOS, False if denied.
        """
        try:
            import platform
            if platform.system() != "Darwin":
                return True  # Not on macOS, no permission check needed
                
            # On macOS, try to check accessibility permissions more carefully
            try:
                # Try to use a system call to check if we have accessibility permissions
                import subprocess
                result = subprocess.run(
                    ["osascript", "-e", "tell application \"System Events\" to get name of every process"],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    logger.info("Accessibility permissions appear to be granted")
                    return True
                else:
                    logger.warning("Accessibility permissions may not be granted")
                    return False
            except Exception as e:
                logger.warning(f"Could not check accessibility permissions via osascript: {e}")
                
            # Fallback: try a very simple pynput test
            from pynput import keyboard
            
            # Don't actually start a listener, just create one to test
            try:
                test_listener = keyboard.Listener(on_press=lambda key: None)
                # Don't start it, just creating it shouldn't crash
                del test_listener
                return True
            except Exception as e:
                logger.error(f"pynput listener creation failed: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Accessibility permissions check failed: {e}")
            return False
