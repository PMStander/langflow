"""Component List for the AI Assistant.

This module provides the ComponentList class that manages a list of components
and provides methods to retrieve them.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from langflow.services.settings.service import SettingsService


class ComponentList:
    """A class to manage a list of components.

    This class provides methods to retrieve components by type, name, or all components.
    """

    def __init__(self):
        """Initialize the ComponentList."""
        self.components: Dict[str, Dict[str, Any]] = {}
        self.initialized = False

    def initialize(self, settings_service: Optional["SettingsService"] = None) -> None:
        """Initialize the component list.

        Args:
            settings_service: The settings service for accessing component paths.
        """
        if self.initialized:
            return

        # Import here to avoid circular imports
        from langflow.interface.components import get_all_components
        from langflow.services.deps import get_settings_service

        if settings_service is None:
            settings_service = get_settings_service()

        # Get all components
        components = get_all_components(settings_service.settings.components_path, as_dict=True)
        self.components = components
        self.initialized = True

    def get_component(self, component_name: str) -> Optional[Any]:
        """Get a component by name.

        Args:
            component_name: The name of the component.

        Returns:
            The component if found, None otherwise.
        """
        if not self.initialized:
            self.initialize()

        return self.components.get(component_name)

    def get_components_by_type(self, component_type: str) -> List[Any]:
        """Get all components of a specific type.

        Args:
            component_type: The type of components to retrieve.

        Returns:
            A list of components of the specified type.
        """
        if not self.initialized:
            self.initialize()

        result = []
        for component in self.components.values():
            if component.get("type", "").lower() == component_type.lower():
                result.append(component)

        return result

    def get_all_components(self) -> List[Any]:
        """Get all components.

        Returns:
            A list of all components.
        """
        if not self.initialized:
            self.initialize()

        return list(self.components.values())
