"""Factory for the Supabase Auth Service."""

from typing_extensions import override

from langflow.services.factory import ServiceFactory
from langflow.services.schema import ServiceType
from langflow.services.settings.service import SettingsService
from langflow.services.supabase_auth.service import SupabaseAuthService


class SupabaseAuthServiceFactory(ServiceFactory):
    """Factory for creating Supabase Auth Service instances."""

    def __init__(self) -> None:
        super().__init__(SupabaseAuthService)

    @override
    def create(self, settings_service: SettingsService) -> SupabaseAuthService:
        """Create a new Supabase Auth Service instance.

        Args:
            settings_service: The settings service.

        Returns:
            SupabaseAuthService: A new Supabase Auth Service instance.
        """
        return SupabaseAuthService(settings_service)
