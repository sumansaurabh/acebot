import json
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Settings for the LLM service."""

    model: str = "gpt-4o"
    temperature: float = 1
    max_retries: int = 3
    timeout: int = 60
    # Use streaming for more responsive output
    streaming: bool = False

    # API key should be stored securely, not in config
    api_key_env_var: str = "OPENAI_API_KEY"

    model_config = SettingsConfigDict(env_prefix="INTERVIEW_CORVUS_LLM_")


class UISettings(BaseSettings):
    """Settings for the user interface."""

    default_theme: str = "dark"
    default_font_size: int = 12
    default_window_opacity: float = 0.9
    default_window_size: Dict[str, int] = Field(
        default_factory=lambda: {"width": 600, "height": 400}
    )
    always_on_top: bool = True  # Default to always on top
    model_config = SettingsConfigDict(env_prefix="INTERVIEW_CORVUS_UI_")


class HotkeySettings(BaseSettings):
    """Settings for application hotkeys."""

    screenshot_key: str = "Cmd+Ctrl+1"  # macOS style
    generate_solution_key: str = "Cmd+Ctrl+2"
    toggle_visibility_key: str = "Cmd+Ctrl+B"
    move_window_keys: Dict[str, str] = Field(
        default_factory=lambda: {
            "up": "Cmd+Up",
            "down": "Cmd+Down",
            "left": "Cmd+Left",
            "right": "Cmd+Right",
        }
    )
    optimize_solution_key: str = "Cmd+Ctrl+O"
    reset_history_key: str = "Cmd+Ctrl+R"
    panic_key: str = "Cmd+Q"

    model_config = SettingsConfigDict(env_prefix="INTERVIEW_CORVUS_HOTKEY_")


class PromptTemplates(BaseSettings):
    """Settings for prompt templates."""

    templates: Dict[str, str] = Field(
        default_factory=lambda: {
            "code_solution": """
            Please analyze the following programming problem and provide a solution:

            {problem_description}

            Provide a comprehensive solution in {language} programming language.

            Your response should include:
            1. Complete code solution
            2. Step-by-step explanation of your approach
            3. Analysis of time complexity (Big O notation)
            4. Analysis of space complexity (Big O notation)
            5. Identification of edge cases and how they are handled
            6. (Optional) Alternative approaches with brief descriptions

            Focus on writing efficient, clean, and well-documented code.
            """,
            "code_optimization": """
            Please analyze and optimize the following {language} code:

            ```{language}
            {code}
            ```

            Provide a comprehensive optimization by:
            1. Identifying performance bottlenecks
            2. Improving time and/or space complexity
            3. Enhancing code readability and maintainability
            4. Fixing any bugs or edge cases

            Your response should include:
            1. The original code
            2. The optimized code
            3. A list of specific improvements made
            4. Time complexity analysis (before and after)
            5. Space complexity analysis (before and after)
            6. Detailed explanation of your optimization process

            Focus on meaningful optimizations that significantly improve performance or code quality.
            """,
            "complexity_analysis": """
            Please analyze the time and space complexity of the following {language} code:

            ```{language}
            {code}
            ```

            Provide a detailed analysis of:
            1. The overall time complexity with explanation
            2. The overall space complexity with explanation
            3. Analysis of each significant part of the algorithm
            4. Potential bottlenecks
            5. Suggestions for improving efficiency

            Be precise in your Big O notation and explain your reasoning.
            """,
            "screenshot_solution": """
            Please analyze the programming problem shown in the screenshot and provide a solution.

            Provide a comprehensive solution in {language} programming language.

            Your response should include:
            1. Complete code solution
            2. Step-by-step explanation of your approach
            3. Analysis of time complexity (Big O notation)
            4. Analysis of space complexity (Big O notation)
            5. Identification of edge cases and how they are handled
            6. (Optional) Alternative approaches with brief descriptions

            Focus on writing efficient, clean, and well-documented code.
            """,
            "ocr_text_solution": """
            Please analyze the following programming problem extracted from a screenshot and provide a solution:

            {ocr_text}

            Provide a comprehensive solution in {language} programming language.

            Your response should include:
            1. Complete code solution
            2. Step-by-step explanation of your approach
            3. Analysis of time complexity (Big O notation)
            4. Analysis of space complexity (Big O notation)
            5. Identification of edge cases and how they are handled
            6. (Optional) Alternative approaches with brief descriptions

            If there seem to be any OCR errors or unclear parts in the problem description, 
            please make your best guess and note your assumptions.

            Focus on writing efficient, clean, and well-documented code.
            """,
        }
    )

    model_config = SettingsConfigDict(env_prefix="INTERVIEW_CORVUS_PROMPTS_")


class Settings(BaseSettings):
    """Main application settings."""

    app_name: str = "Interview Coder"
    app_data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".interview_corvus"
    )
    debug_mode: bool = True

    # Default programming language
    default_language: str = "python"

    # Available programming languages
    available_languages: List[str] = Field(
        default_factory=lambda: [
            "python",
            "java",
            "javascript",
            "c++",
            "c#",
            "go",
            "rust",
            "ruby",
        ]
    )

    # Sub-settings
    llm: LLMSettings = Field(default_factory=LLMSettings)
    ui: UISettings = Field(default_factory=UISettings)
    hotkeys: HotkeySettings = Field(default_factory=HotkeySettings)
    prompts: PromptTemplates = Field(default_factory=PromptTemplates)

    @field_validator("app_data_dir", mode="before")
    @classmethod
    def create_app_dir(cls, v):
        """Create application data directory if it doesn't exist."""
        dir_path = Path(v)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="INTERVIEW_CORVUS_",
    )

    def save_user_settings(self):
        """Save user-specific settings to a JSON file."""
        settings_path = self.app_data_dir / "user_settings.json"

        user_settings = {
            "default_language": self.default_language,
            "llm": {
                "model": self.llm.model,
                "temperature": self.llm.temperature,
                "streaming": self.llm.streaming,
            },
            "ui": {
                "default_theme": self.ui.default_theme,
                "default_window_opacity": self.ui.default_window_opacity,
            },
            "prompts": {"templates": self.prompts.templates},
        }

        # Save to JSON
        with open(settings_path, "w") as f:
            json.dump(user_settings, f, indent=2)

    def load_user_settings(self):
        """Load user-specific settings from a JSON file."""
        settings_path = self.app_data_dir / "user_settings.json"

        # Check if settings file exists
        if not settings_path.exists():
            return

        try:
            with open(settings_path, "r") as f:
                user_settings = json.load(f)

            if "default_language" in user_settings:
                self.default_language = user_settings["default_language"]

            if "llm" in user_settings:
                llm_settings = user_settings["llm"]
                if "model" in llm_settings:
                    self.llm.model = llm_settings["model"]
                if "temperature" in llm_settings:
                    self.llm.temperature = llm_settings["temperature"]
                if "streaming" in llm_settings:
                    self.llm.streaming = llm_settings["streaming"]

            if "ui" in user_settings:
                ui_settings = user_settings["ui"]
                if "default_theme" in ui_settings:
                    self.ui.default_theme = ui_settings["default_theme"]
                if "default_window_opacity" in ui_settings:
                    self.ui.default_window_opacity = ui_settings[
                        "default_window_opacity"
                    ]

            if "prompts" in user_settings and "templates" in user_settings["prompts"]:
                self.prompts.templates = user_settings["prompts"]["templates"]

        except Exception as e:
            logger.info(f"Error loading user settings: {e}")


# Create global settings instance
settings = Settings()

settings.load_user_settings()
