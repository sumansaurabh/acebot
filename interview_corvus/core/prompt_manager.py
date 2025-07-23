"""Manager for generating prompts for different tasks."""

from interview_corvus.config import settings


class PromptManager:
    """Manager for generating prompts for various tasks."""

    def __init__(self):
        """Initialize the prompt manager with templates."""
        # Use templates from settings which includes user customizations
        self.templates = settings.prompts.templates.copy()

    def get_prompt(self, prompt_type: str, **kwargs) -> str:
        """
        Generate a prompt based on a template and parameters.

        Args:
            prompt_type: Type of prompt ("code_solution", "code_optimization", etc.)
            **kwargs: Parameters to substitute in the template

        Returns:
            The generated prompt text

        Raises:
            ValueError: If the prompt type is unknown
        """
        if prompt_type not in self.templates:
            print(f"Available prompt types: {list(self.templates.keys())}")
            print(self.templates)
            raise ValueError(f"Unknown prompt type: {prompt_type}")

        return self.templates[prompt_type].format(**kwargs)

    def add_custom_template(self, name: str, template: str) -> None:
        """
        Add a custom prompt template.

        Args:
            name: Name of the template
            template: Template string with placeholders
        """
        self.templates[name] = template

        # Update settings templates to persist between sessions
        settings.prompts.templates[name] = template
        settings.save_user_settings()

    def update_template(self, name: str, template: str) -> None:
        """
        Update an existing prompt template.

        Args:
            name: Name of the template to update
            template: New template string with placeholders

        Raises:
            ValueError: If template name doesn't exist
        """
        if name not in self.templates:
            raise ValueError(f"Template '{name}' does not exist")

        self.templates[name] = template

        # Update settings templates to persist between sessions
        settings.prompts.templates[name] = template
        settings.save_user_settings()

    def get_template(self, name: str) -> str:
        """
        Get a template by name.

        Args:
            name: Name of the template

        Returns:
            The template string

        Raises:
            ValueError: If template name doesn't exist
        """
        if name not in self.templates:
            raise ValueError(f"Template '{name}' does not exist")

        return self.templates[name]

    def get_all_template_names(self) -> list:
        """
        Get a list of all available template names.

        Returns:
            List of template names
        """
        return list(self.templates.keys())
