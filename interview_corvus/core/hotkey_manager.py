import sys

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
        self._convert_hotkeys_to_pynput_format()

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
                    # On macOS, Cmd typically corresponds to Ctrl in PyQt
                    if sys.platform == "darwin":
                        keys_set.add(keyboard.Key.cmd)
                    else:
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
        # Регистрируем локальные шорткаты через PyQt
        self.shortcuts.clear()

        for key_sequence, signal in self.hotkeys.items():
            shortcut = QShortcut(QKeySequence(key_sequence), window)

            def create_callback(sig):
                return lambda: sig.emit() if isinstance(sig, pyqtBoundSignal) else sig()

            callback = create_callback(signal)
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)

        logger.info(f"Зарегистрировано {len(self.shortcuts)} локальных горячих клавиш")

        # Запускаем глобальный обработчик pynput
        self.start_global_listener()

    def start_global_listener(self):
        """Запускает прослушивание глобальных горячих клавиш с помощью pynput."""
        if self.key_listener is not None and self.key_listener.is_alive():
            logger.info("Глобальный обработчик горячих клавиш уже запущен")
            return

        # Обновляем множество интересующих нас клавиш
        for keys_set in self.pynput_hotkeys.keys():
            for key in keys_set:
                self.keys_of_interest.add(key)

        # Запускаем прослушиватель клавиатуры
        self.key_listener = keyboard.Listener(
            on_press=self.on_key_press, on_release=self.on_key_release
        )
        self.key_listener.start()
        logger.info("Запущен глобальный обработчик горячих клавиш")

    def stop_global_listener(self):
        """Останавливает прослушивание глобальных горячих клавиш."""
        if self.key_listener and self.key_listener.is_alive():
            self.key_listener.stop()
            logger.info("Глобальный обработчик горячих клавиш остановлен")

    def on_key_press(self, key):
        """Handler for key press events from pynput."""
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
                    logger.info(f"Error triggering signal: {e}")
                    import traceback

                    logger.info(traceback.format_exc())

    def on_key_release(self, key):
        """Handler for key release events from pynput."""
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

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Filter application events to detect hotkey combinations (backup method).
        Только для внутриоконных шорткатов и как резервный механизм.

        Args:
            obj: The object that received the event
            event: The event that was received

        Returns:
            True if the event was handled, False otherwise
        """
        # Для внутреннего использования в приложении - оставляем как запасной вариант
        return super().eventFilter(obj, event)
