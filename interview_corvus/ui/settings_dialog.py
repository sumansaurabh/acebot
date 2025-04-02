from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from interview_corvus.config import PromptTemplates, settings
from interview_corvus.core.prompt_manager import PromptManager
from interview_corvus.security.api_key_manager import APIKeyManager


class SettingsDialog(QDialog):
    """
    Dialog for configuring application settings.
    """

    def __init__(self, parent=None):
        """
        Initialize the settings dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.api_key_manager = APIKeyManager()
        self.prompt_manager = PromptManager()

        self.setWindowTitle("Settings")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create a tab widget for better organization
        self.tab_widget = QTabWidget()

        # General tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        # Language selection
        language_group = QGroupBox("Programming Language")
        language_layout = QFormLayout()

        self.language_combo = QComboBox()
        self.language_combo.addItems(settings.available_languages)
        language_layout.addRow("Default Language:", self.language_combo)

        language_group.setLayout(language_layout)
        general_layout.addWidget(language_group)

        # Add the general tab
        self.tab_widget.addTab(general_tab, "General")

        # LLM Settings tab
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)

        # LLM Settings
        llm_group = QGroupBox("LLM Settings")
        llm_form_layout = QFormLayout()

        # API Provider
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        llm_form_layout.addRow("API Provider:", self.provider_combo)

        # Model selection
        self.model_combo = QComboBox()
        # OpenAI models by default
        self.model_combo.addItems(["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"])
        llm_form_layout.addRow("Model:", self.model_combo)

        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Your API key")
        llm_form_layout.addRow("API Key:", self.api_key_input)

        # Show API Key checkbox
        self.show_api_key = QCheckBox("Show API Key")
        self.show_api_key.stateChanged.connect(self.toggle_api_key_visibility)
        llm_form_layout.addRow("", self.show_api_key)

        # Temperature
        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setRange(0.0, 2.0)
        self.temperature_input.setSingleStep(0.1)
        self.temperature_input.setDecimals(1)
        self.temperature_input.setValue(1.0)
        llm_form_layout.addRow("Temperature:", self.temperature_input)

        # Test connection button
        self.test_connection_button = QPushButton("Check connection")
        self.test_connection_button.clicked.connect(self.test_connection)
        llm_form_layout.addRow("", self.test_connection_button)

        llm_group.setLayout(llm_form_layout)
        llm_layout.addWidget(llm_group)

        # Add the LLM tab
        self.tab_widget.addTab(llm_tab, "LLM Settings")

        # Prompts tab
        prompts_tab = QWidget()
        prompts_layout = QVBoxLayout(prompts_tab)

        # Prompt editor
        prompt_group = QGroupBox("Prompt Templates")
        prompt_layout = QVBoxLayout()

        # List of available prompts
        prompt_select_layout = QHBoxLayout()
        prompt_select_layout.addWidget(QLabel("Available Templates:"))

        self.prompt_list = QListWidget()
        self.prompt_list.addItems(self.prompt_manager.get_all_template_names())
        self.prompt_list.currentTextChanged.connect(self.on_prompt_selected)
        prompt_select_layout.addWidget(self.prompt_list)
        prompt_layout.addLayout(prompt_select_layout)

        # Template editor
        self.prompt_editor = QTextEdit()
        self.prompt_editor.setPlaceholderText("Select a template to edit")
        prompt_layout.addWidget(self.prompt_editor)

        # Save template button
        self.save_prompt_button = QPushButton("Save Template")
        self.save_prompt_button.clicked.connect(self.save_prompt_template)
        prompt_layout.addWidget(self.save_prompt_button)

        # Reset to default button
        self.reset_prompt_button = QPushButton("Reset to Default")
        self.reset_prompt_button.clicked.connect(self.reset_prompt_template)
        prompt_layout.addWidget(self.reset_prompt_button)

        prompt_group.setLayout(prompt_layout)
        prompts_layout.addWidget(prompt_group)

        # Add the prompts tab
        self.tab_widget.addTab(prompts_tab, "Prompts")

        # Add tab widget to main layout
        layout.addWidget(self.tab_widget)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

    def load_settings(self):
        """Load current settings into the UI."""
        # Default programming language
        index = self.language_combo.findText(settings.default_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        # Default to OpenAI
        self.provider_combo.setCurrentText("OpenAI")

        # LLM settings
        self.model_combo.setCurrentText(settings.llm.model)
        self.temperature_input.setValue(settings.llm.temperature)

        # Get API key if it exists
        try:
            api_key = self.api_key_manager.get_api_key()
            if api_key:
                self.api_key_input.setText(api_key)
        except (ValueError, Exception) as e:
            logger.info(f"Could not load API key: {e}")
            # No API key exists

    def save_settings(self):
        """Save settings from the UI."""
        # Save language setting
        settings.default_language = self.language_combo.currentText()

        # Save LLM settings
        settings.llm.model = self.model_combo.currentText()
        settings.llm.temperature = self.temperature_input.value()

        # Save API key
        api_key = self.api_key_input.text().strip()
        if api_key:
            try:
                self.api_key_manager.set_api_key(api_key)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error saving API key: {e}")

        try:
            settings.save_user_settings()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving settings: {e}")

        # Close dialog
        self.accept()

    def on_provider_changed(self, provider):
        """
        Handle provider change.

        Args:
            provider: The selected provider name
        """
        self.model_combo.clear()

        if provider == "OpenAI":
            self.model_combo.addItems(
                ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
            )
            self.api_key_input.setPlaceholderText("Enter OpenAI API key")
        elif provider == "Anthropic":
            self.model_combo.addItems(
                ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
            )
            self.api_key_input.setPlaceholderText("Enter Anthropic API key")

    def toggle_api_key_visibility(self, state):
        """
        Toggle API key visibility.

        Args:
            state: Checkbox state
        """
        if state == Qt.CheckState.Checked:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

    def test_connection(self):
        """Test connection to the LLM API."""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Error", "Please enter an API key.")
            return

        # Temporarily save API key for testing
        try:
            old_api_key = self.api_key_manager.get_api_key()
            self.api_key_manager.set_api_key(api_key)

            self.test_connection_button.setEnabled(False)
            self.test_connection_button.setText("Checking connection...")
            QApplication.processEvents()  # Update UI

            # Import appropriate library based on provider
            if self.provider_combo.currentText() == "OpenAI":
                from openai import OpenAI

                client = OpenAI(api_key=api_key)
                client.chat.completions.create(
                    model=self.model_combo.currentText(),
                    messages=[{"role": "user", "content": "Hello, are you working?"}],
                    max_tokens=5,
                )
            else:  # Anthropic
                from anthropic import Anthropic

                client = Anthropic(api_key=api_key)
                client.messages.create(
                    model=self.model_combo.currentText(),
                    max_tokens=5,
                    messages=[{"role": "user", "content": "Hello, are you working?"}],
                )

            if old_api_key:
                self.api_key_manager.set_api_key(old_api_key)

            QMessageBox.information(self, "Success", "Connection successful!")

        except Exception as e:
            if old_api_key:
                self.api_key_manager.set_api_key(old_api_key)

            QMessageBox.critical(self, "Error", f"Cannot connect to API: {str(e)}")
        finally:
            self.test_connection_button.setEnabled(True)
            self.test_connection_button.setText("Check connection")

    def on_prompt_selected(self, template_name):
        """
        Handle prompt template selection.

        Args:
            template_name: The name of the selected template
        """
        if not template_name:
            self.prompt_editor.clear()
            self.prompt_editor.setPlaceholderText("Select a template to edit")
            return

        try:
            template_text = self.prompt_manager.get_template(template_name)
            self.prompt_editor.setText(template_text)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def save_prompt_template(self):
        """Save the current prompt template."""
        current_template = self.prompt_list.currentItem()
        if not current_template:
            QMessageBox.warning(self, "Error", "Please select a template to save")
            return

        template_name = current_template.text()
        template_text = self.prompt_editor.toPlainText()

        if not template_text.strip():
            QMessageBox.warning(self, "Error", "Template cannot be empty")
            return

        try:
            self.prompt_manager.update_template(template_name, template_text)
            QMessageBox.information(
                self, "Success", f"Template '{template_name}' saved successfully"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving template: {str(e)}")

    def reset_prompt_template(self):
        """Reset the current prompt template to default."""
        current_template = self.prompt_list.currentItem()
        if not current_template:
            QMessageBox.warning(self, "Error", "Please select a template to reset")
            return

        template_name = current_template.text()

        # Confirm reset
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            f"Are you sure you want to reset the '{template_name}' template to default?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Get default template from initial settings
        default_templates = PromptTemplates().templates
        if template_name in default_templates:
            default_template = default_templates[template_name]
            self.prompt_editor.setText(default_template)
            self.prompt_manager.update_template(template_name, default_template)
            QMessageBox.information(
                self, "Success", f"Template '{template_name}' reset to default"
            )
        else:
            QMessageBox.warning(
                self, "Error", f"No default template found for '{template_name}'"
            )
