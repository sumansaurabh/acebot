import json
import sys
from pathlib import Path
from typing import Dict, List

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
    api_key_env_var: str = "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"

    model_config = SettingsConfigDict(env_prefix="INTERVIEW_CORVUS_LLM_")


class UISettings(BaseSettings):
    """Settings for the user interface."""

    default_theme: str = "dark"
    default_font_size: int = 12
    default_window_opacity: float = 1
    default_window_size: Dict[str, int] = Field(
        default_factory=lambda: {"width": 600, "height": 400}
    )
    always_on_top: bool = True  # Default to always on top
    model_config = SettingsConfigDict(env_prefix="INTERVIEW_CORVUS_UI_")


class HotkeySettings(BaseSettings):
    """Settings for application hotkeys."""

    # Properties for platform-specific defaults
    @property
    def default_screenshot_key(self):
        return "Cmd+Ctrl+1" if sys.platform == "darwin" else "Ctrl+Alt+1"

    @property
    def default_generate_solution_key(self):
        return "Cmd+Ctrl+2" if sys.platform == "darwin" else "Ctrl+Alt+2"

    @property
    def default_toggle_visibility_key(self):
        return "Cmd+Ctrl+B" if sys.platform == "darwin" else "Ctrl+Alt+B"

    @property
    def default_move_window_keys(self):
        return {
            "up": "Cmd+Up" if sys.platform == "darwin" else "Win+Up",
            "down": "Cmd+Down" if sys.platform == "darwin" else "Win+Down",
            "left": "Cmd+Left" if sys.platform == "darwin" else "Win+Left",
            "right": "Cmd+Right" if sys.platform == "darwin" else "Win+Right",
        }

    @property
    def default_optimize_solution_key(self):
        return "Cmd+Ctrl+O" if sys.platform == "darwin" else "Ctrl+Alt+O"

    @property
    def default_reset_history_key(self):
        return "Cmd+Ctrl+R" if sys.platform == "darwin" else "Ctrl+Alt+R"

    @property
    def default_panic_key(self):
        return "Cmd+Q" if sys.platform == "darwin" else "Alt+Q"

    # Actual configurable values with defaults
    screenshot_key: str = Field(
        default_factory=lambda: "Cmd+Ctrl+1"
        if sys.platform == "darwin"
        else "Ctrl+Alt+1"
    )
    generate_solution_key: str = Field(
        default_factory=lambda: "Cmd+Ctrl+2"
        if sys.platform == "darwin"
        else "Ctrl+Alt+2"
    )
    toggle_visibility_key: str = Field(
        default_factory=lambda: "Cmd+Ctrl+B"
        if sys.platform == "darwin"
        else "Ctrl+Alt+B"
    )
    move_window_keys: Dict[str, str] = Field(
        default_factory=lambda: {
            "up": "Cmd+Up" if sys.platform == "darwin" else "Win+Up",
            "down": "Cmd+Down" if sys.platform == "darwin" else "Win+Down",
            "left": "Cmd+Left" if sys.platform == "darwin" else "Win+Left",
            "right": "Cmd+Right" if sys.platform == "darwin" else "Win+Right",
        }
    )
    optimize_solution_key: str = Field(
        default_factory=lambda: "Cmd+Ctrl+O"
        if sys.platform == "darwin"
        else "Ctrl+Alt+O"
    )
    reset_history_key: str = Field(
        default_factory=lambda: "Cmd+Ctrl+R"
        if sys.platform == "darwin"
        else "Ctrl+Alt+R"
    )
    panic_key: str = Field(
        default_factory=lambda: "Cmd+Q" if sys.platform == "darwin" else "Alt+Q"
    )

    def reset_to_defaults(self):
        """Reset all hotkeys to their platform-specific defaults."""
        self.screenshot_key = self.default_screenshot_key
        self.generate_solution_key = self.default_generate_solution_key
        self.toggle_visibility_key = self.default_toggle_visibility_key
        self.move_window_keys = self.default_move_window_keys.copy()
        self.optimize_solution_key = self.default_optimize_solution_key
        self.reset_history_key = self.default_reset_history_key
        self.panic_key = self.default_panic_key

    model_config = SettingsConfigDict(env_prefix="INTERVIEW_CORVUS_HOTKEY_")


class PromptTemplates(BaseSettings):
    """Settings for prompt templates."""

    templates: Dict[str, str] = Field(
        default_factory=lambda: {
            # not being used
            "code_solution": """
            Please analyze the following programming problem and provide a solution:

            {problem_description}

            Provide a solution in {language} programming language.

            Your response should include:
            1. Complete code solution
            2. Concise approach explanation focusing only on the core solution strategy
            3. Analysis of time complexity (Big O notation)
            4. Analysis of space complexity (Big O notation)
            5. Identification of edge cases and how they are handled
            6. (Optional) Alternative approaches with brief descriptions

            For the explanation, focus only on the key algorithmic approach and logic, not problem statement details.
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
            "mcq_solution": """
I have a multiple-choice question. Please act as an expert tutor and solve it step by step. First, understand and interpret the question. Then, evaluate each option carefully. Identify the correct answer and explain why it is correct. Also, briefly explain why the other options are incorrect.

If any background knowledge or assumptions are needed, state them explicitly. Use clear and logical reasoning.""",
            "screenshot_solution": """
            Please analyze the programming problem shown in the screenshot and provide a solution.

            Very important: **Provide a solution in {language} programming language. Do not choose any other language for the response**


            Your response should include:
            1. Complete code solution
            2. Concise approach explanation focusing only on the core solution strategy
            3. **Add very heavy documentation of the code**
            4. Analysis of time complexity (Big O notation)
            5. Analysis of space complexity (Big O notation)
            6. Identification of edge cases and how they are handled
            7. (Optional) Alternative approaches with brief descriptions


            For the explanation, focus only on the key algorithmic approach and logic, not problem statement details.
            """,
            "mcq": """
            
You are an expert MCQ solver. You will be shown an image containing **one or more multiple-choice questions**. For each question in the image:

1. **Determine whether it is single-choice or multiple-choice**
2. **Identify the correct answer(s)**
3. **Return only the correct option letter(s) with the option text**
4. **Add a short explanation for why each option is correct**

---

### ✏️ Output Format (strictly follow this for each question):

```
Q<n>. <Question text (optional)>

<letter>: <Correct option text>  
<letter>: <Correct option text>  

Explanation: <Clear, concise explanation for why this is the correct answer. If multiple answers, explain each briefly.>
```

**Notes:**

* Use `Q1`, `Q2`, etc. to label each question
* If only one correct answer, return just one line under it
* If multiple correct answers, return all correct options
* Always follow with `Explanation:` line (mandatory)
* Do not include any unrelated text, instructions, or wrong options

---

### ✅ Example Output:

```
Q1. What are prime numbers less than 10?

b: 2  
c: 3  
d: 7  

Explanation: 2, 3, and 7 are all prime numbers less than 10. Prime numbers are only divisible by 1 and themselves.
```

```
Q2. What is the powerhouse of the cell?

a: Mitochondria  

Explanation: The mitochondria generate most of the cell’s energy through respiration, hence called the powerhouse.
```

            """,
            # not being used
            "ocr_text_solution": """
            Please analyze the following programming problem extracted from a screenshot and provide a solution:

            {ocr_text}

            Provide a solution in {language} programming language.

            Your response should include:
            1. Complete code solution
            2. Concise approach explanation focusing only on the core solution strategy
            3. Analysis of time complexity (Big O notation)
            4. Analysis of space complexity (Big O notation)
            5. Identification of edge cases and how they are handled
            6. (Optional) Alternative approaches with brief descriptions

            If there seem to be any OCR errors or unclear parts in the problem description, 
            please make your best guess and note your assumptions.

            For the explanation, focus only on the key algorithmic approach and logic, not problem statement details.
            """,
        }
    )

    model_config = SettingsConfigDict(env_prefix="INTERVIEW_CORVUS_PROMPTS_")


class Settings(BaseSettings):
    """Main application settings."""

    app_name: str = "AceBot"
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
            "mysql",
            "mcq"
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
                "always_on_top": self.ui.always_on_top,
            },
            "hotkeys": {
                "screenshot_key": self.hotkeys.screenshot_key,
                "generate_solution_key": self.hotkeys.generate_solution_key,
                "toggle_visibility_key": self.hotkeys.toggle_visibility_key,
                "move_window_keys": self.hotkeys.move_window_keys,
                "optimize_solution_key": self.hotkeys.optimize_solution_key,
                "reset_history_key": self.hotkeys.reset_history_key,
                "panic_key": self.hotkeys.panic_key,
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
                if "always_on_top" in ui_settings:
                    self.ui.always_on_top = ui_settings["always_on_top"]

            # Load hotkey settings
            if "hotkeys" in user_settings:
                hotkey_settings = user_settings["hotkeys"]
                if "screenshot_key" in hotkey_settings:
                    self.hotkeys.screenshot_key = hotkey_settings["screenshot_key"]
                if "generate_solution_key" in hotkey_settings:
                    self.hotkeys.generate_solution_key = hotkey_settings[
                        "generate_solution_key"
                    ]
                if "toggle_visibility_key" in hotkey_settings:
                    self.hotkeys.toggle_visibility_key = hotkey_settings[
                        "toggle_visibility_key"
                    ]
                if "move_window_keys" in hotkey_settings:
                    self.hotkeys.move_window_keys = hotkey_settings["move_window_keys"]
                if "optimize_solution_key" in hotkey_settings:
                    self.hotkeys.optimize_solution_key = hotkey_settings[
                        "optimize_solution_key"
                    ]
                if "reset_history_key" in hotkey_settings:
                    self.hotkeys.reset_history_key = hotkey_settings[
                        "reset_history_key"
                    ]
                if "panic_key" in hotkey_settings:
                    self.hotkeys.panic_key = hotkey_settings["panic_key"]

            if "prompts" in user_settings and "templates" in user_settings["prompts"]:
                self.prompts.templates = user_settings["prompts"]["templates"]

        except Exception as e:
            logger.info(f"Error loading user settings: {e}")


# Create global settings instance
settings = Settings()

settings.load_user_settings()
