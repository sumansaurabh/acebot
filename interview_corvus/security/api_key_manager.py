import os

import keyring

from interview_corvus.config import settings


class APIKeyManager:
    """Manages secure storage and retrieval of API keys."""

    SERVICE_NAME = "interview_corvus"

    def __init__(self):
        """Initialize the API key manager."""
        self.env_var_name = self._get_env_var_name()

    def _get_env_var_name(self):
        """Get the appropriate environment variable name based on the model."""
        if any(
            model_prefix in settings.llm.model
            for model_prefix in ["claude", "anthropic"]
        ):
            return "ANTHROPIC_API_KEY"
        else:
            return "OPENAI_API_KEY"

    def get_api_key(self) -> str:
        """
        Get the API key from environment variable, config, or keyring.

        Returns:
            str: The API key

        Raises:
            ValueError: If API key cannot be found
        """
        # First try environment variable
        api_key = os.environ.get(self.env_var_name)
        if api_key:
            return api_key

        # Check if it's stored in config (fallback for development)
        if hasattr(settings.llm, 'api_key_env_var') and settings.llm.api_key_env_var.startswith('sk-'):
            return settings.llm.api_key_env_var

        # Then try keyring
        api_key = keyring.get_password(self.SERVICE_NAME, self.env_var_name)
        if api_key:
            return api_key

        # If no key is found, prompt the user
        return ""

    def set_api_key(self, api_key: str) -> None:
        """
        Store the API key in the system's secure keyring.

        Args:
            api_key: The API key to store
        """
        keyring.set_password(self.SERVICE_NAME, self.env_var_name, api_key)
