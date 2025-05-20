"""Factory for the AI Assistant Service."""

from langflow.services.ai_assistant.service import AIAssistantService
from langflow.services.factory import ServiceFactory
from langflow.services.deps import get_settings_service


class AIAssistantServiceFactory(ServiceFactory):
    """Factory for creating AI Assistant Service instances."""

    def __init__(self):
        """Initialize the AI Assistant Service Factory."""
        super().__init__(AIAssistantService)

    def create(self, settings_service=None) -> AIAssistantService:
        """Create a new AI Assistant Service instance.

        Args:
            settings_service: The settings service to use.

        Returns:
            AIAssistantService: A new AI Assistant Service instance.
        """
        if settings_service is None:
            settings_service = get_settings_service()
        return AIAssistantService(settings_service)
