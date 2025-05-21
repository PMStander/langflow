"""Flow Constructor for the AI Assistant.

This module provides the FlowConstructor class that builds flows based on parsed instructions.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from loguru import logger
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from langflow.services.ai_assistant.knowledge_base import ComponentKnowledgeBase
    from langflow.services.ai_assistant.instruction_parser import ParsedInstruction, ComponentRequirement, ConnectionRequirement


class FlowNode(BaseModel):
    """A node in a flow.

    This class represents a node in a flow, including its ID, position, data, and other properties.
    """

    id: str = Field(..., description="The unique identifier of the node")
    type: str = Field(..., description="The type of the node")
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0}, description="The position of the node")
    data: Dict[str, Any] = Field(..., description="The data of the node")
    width: Optional[int] = Field(None, description="The width of the node")
    height: Optional[int] = Field(None, description="The height of the node")
    selected: bool = Field(False, description="Whether the node is selected")
    positionAbsolute: Optional[Dict[str, float]] = Field(None, description="The absolute position of the node")
    dragging: bool = Field(False, description="Whether the node is being dragged")


class FlowEdge(BaseModel):
    """An edge in a flow.

    This class represents an edge in a flow, including its ID, source, target, and other properties.
    """

    id: str = Field(..., description="The unique identifier of the edge")
    source: str = Field(..., description="The ID of the source node")
    target: str = Field(..., description="The ID of the target node")
    sourceHandle: Optional[str] = Field(None, description="The handle of the source node")
    targetHandle: Optional[str] = Field(None, description="The handle of the target node")
    data: Dict[str, Any] = Field(default_factory=dict, description="The data of the edge")
    selected: bool = Field(False, description="Whether the edge is selected")


class Flow(BaseModel):
    """A flow.

    This class represents a flow, including its nodes and edges.
    """

    nodes: List[FlowNode] = Field(default_factory=list, description="The nodes in the flow")
    edges: List[FlowEdge] = Field(default_factory=list, description="The edges in the flow")


class FlowConstructor:
    """Constructor for flows based on parsed instructions.

    This class builds flows based on parsed instructions, including selecting components,
    creating connections, and configuring parameters.
    """

    def __init__(self, knowledge_base: ComponentKnowledgeBase):
        """Initialize the FlowConstructor.

        Args:
            knowledge_base: The component knowledge base.
        """
        self.knowledge_base = knowledge_base

    async def build_flow(self, parsed_instruction: ParsedInstruction) -> Flow:
        """Build a flow from a parsed instruction.

        Args:
            parsed_instruction: The parsed instruction.

        Returns:
            A Flow object containing the nodes and edges.
        """
        logger.info(f"Building flow from parsed instruction: {parsed_instruction.flow_description}")

        try:
            # Select components
            nodes = await self._select_components(parsed_instruction.components)

            # Create connections
            edges = await self._create_connections(parsed_instruction.connections, nodes)

            # Configure parameters
            await self._configure_parameters(parsed_instruction.components, nodes)

            # Position nodes in a visually appealing layout
            await self._position_nodes(nodes)

            # Create the flow
            flow = Flow(nodes=nodes, edges=edges)

            return flow

        except ValueError as e:
            # This is likely an API key error, which we want to propagate to the user
            logger.error(f"API key error while building flow: {str(e)}")
            # Re-raise the error so it can be handled by the API endpoint
            raise
        except Exception as e:
            logger.error(f"Error building flow: {str(e)}")
            # Return an empty flow for other types of errors
            return Flow()

    async def _select_components(self, component_requirements: List[ComponentRequirement]) -> List[FlowNode]:
        """Select components based on requirements.

        Args:
            component_requirements: The component requirements.

        Returns:
            A list of FlowNode objects.
        """
        nodes = []

        # For each component requirement
        for i, requirement in enumerate(component_requirements):
            component_type = requirement.component_type
            component_name = requirement.component_name

            # Get component info from knowledge base
            component_info = await self.knowledge_base.get_component_info(component_type, component_name)

            if not component_info:
                logger.warning(f"Component {component_type}.{component_name} not found in knowledge base")
                continue

            # Create a unique ID for the node
            node_id = f"{component_name}-{uuid.uuid4().hex[:5]}"

            # Create the node data
            node_data = {
                "id": node_id,
                "value": None,
                "type": component_type,
                "node": {
                    "template": component_info.get("template", {}),
                    "description": component_info.get("description", ""),
                    "base_classes": component_info.get("base_classes", []),
                    "display_name": component_info.get("display_name", component_name),
                    "custom_fields": {},
                    "output_types": component_info.get("output_types", []),
                    "documentation": component_info.get("documentation", ""),
                    "input_types": component_info.get("input_types", []),
                    "type": component_type,
                }
            }

            # Create the node
            node = FlowNode(
                id=node_id,
                type="genericNode",
                data=node_data,
                position={"x": 0, "y": i * 100}  # Initial position, will be adjusted later
            )

            nodes.append(node)

        return nodes

    async def _create_connections(self, connection_requirements: List[ConnectionRequirement], nodes: List[FlowNode]) -> List[FlowEdge]:
        """Create connections between components.

        Args:
            connection_requirements: The connection requirements.
            nodes: The nodes in the flow.

        Returns:
            A list of FlowEdge objects.
        """
        edges = []

        # For each connection requirement
        for i, requirement in enumerate(connection_requirements):
            # Get source and target nodes
            if requirement.source_component_idx >= len(nodes) or requirement.target_component_idx >= len(nodes):
                logger.warning(f"Invalid connection requirement: {requirement}")
                continue

            source_node = nodes[requirement.source_component_idx]
            target_node = nodes[requirement.target_component_idx]

            # Get source and target fields
            source_field = requirement.source_field
            target_field = requirement.target_field

            # Create source and target handles
            source_handle = f"{source_node.id}|{source_field}"
            target_handle = f"{target_node.id}|{target_field}"

            # Create edge data
            edge_data = {
                "sourceHandle": {
                    "id": source_handle,
                    "name": source_field,
                    "output_types": source_node.data["node"].get("output_types", [])
                },
                "targetHandle": {
                    "id": target_handle,
                    "fieldName": target_field,
                    "inputTypes": target_node.data["node"].get("input_types", []),
                    "type": "str"  # Default type
                }
            }

            # Create the edge
            edge = FlowEdge(
                id=f"edge-{uuid.uuid4().hex[:5]}",
                source=source_node.id,
                target=target_node.id,
                data=edge_data
            )

            edges.append(edge)

        return edges

    async def _get_api_key(self, key_name: str) -> str:
        """Get an API key from the environment or variable service.

        Args:
            key_name: The name of the API key to get.

        Returns:
            The API key as a string.

        Raises:
            ValueError: If the API key is not found or is set to 'dummy'.
        """
        import os
        from uuid import UUID
        from sqlalchemy.ext.asyncio import AsyncSession

        # Initialize api_key to None at the beginning
        api_key = None
        env_api_key = None
        db_api_key = None

        # Get the API key from environment variables
        env_api_key = os.environ.get(key_name)
        if env_api_key:
            logger.info(f"Found {key_name} in environment variables")
            # Store it but don't use it yet - we'll prioritize the database value
            api_key = env_api_key

        # Try to get the API key from the variable service
        try:
            # Get the variable service
            from langflow.services.deps import get_variable_service, get_session, get_db_service

            # Get the database service and open a session
            db_service = get_db_service()

            async with db_service.with_session() as session:
                # Get the current user directly from the database
                from sqlmodel import select
                from langflow.services.database.models.user.model import User
                from langflow.services.settings.service import SettingsService
                from langflow.services.deps import get_settings_service

                # Get settings to check if AUTO_LOGIN is enabled
                settings_service = get_settings_service()

                # If AUTO_LOGIN is enabled, get the superuser
                if settings_service.auth_settings.AUTO_LOGIN:
                    from langflow.services.database.models.user.crud import get_user_by_username

                    if settings_service.auth_settings.SUPERUSER:
                        user = await get_user_by_username(session, settings_service.auth_settings.SUPERUSER)
                        if user:
                            logger.info(f"Using AUTO_LOGIN superuser: {user.id}")
                        else:
                            logger.warning(f"AUTO_LOGIN enabled but superuser not found")
                else:
                    # Try to get the first user as a fallback
                    stmt = select(User).limit(1)
                    user = (await session.exec(stmt)).first()
                    if user:
                        logger.info(f"Using first available user: {user.id}")
                    else:
                        logger.warning("No users found in database")

                if user:
                    # Get the variable service
                    variable_service = get_variable_service()

                    # List all variables for debugging
                    try:
                        from langflow.services.database.models.variable import Variable

                        # Get all variables for this user
                        stmt = select(Variable).where(Variable.user_id == user.id)
                        all_vars = list((await session.exec(stmt)).all())
                        logger.debug(f"User has {len(all_vars)} variables: {[(v.name, v.type) for v in all_vars]}")
                    except Exception as e:
                        logger.warning(f"Error listing variables: {str(e)}")

                    # Try to get the API key from the variable service
                    try:
                        db_api_key = await variable_service.get_variable(
                            user_id=user.id,
                            name=key_name,
                            field=key_name.lower(),
                            session=session
                        )
                        logger.info(f"Successfully retrieved {key_name} from variable service")
                        logger.debug(f"Value retrieved from variable service for {key_name}: {db_api_key}")

                        # Prioritize the database value over the environment variable
                        if db_api_key and db_api_key != "dummy":
                            api_key = db_api_key
                    except Exception as e:
                        logger.warning(f"Error getting {key_name} from variable service: {str(e)}")
        except Exception as e:
            logger.warning(f"Error accessing variable service: {str(e)}")

        # Check if the API key is missing or set to "dummy"
        if not api_key:
            logger.warning(f"API key {key_name} not found in environment variables or variable service.")
            raise ValueError(f"API key {key_name} not found. Please add your API key in the AI Assistant panel.")
        elif api_key == "dummy":
            logger.warning(f"API key {key_name} is set to 'dummy' in environment variables or variable service.")
            raise ValueError(f"API key {key_name} is set to 'dummy'. Please add your actual API key in the AI Assistant panel.")

        return api_key

    async def _configure_parameters(self, component_requirements: List[ComponentRequirement], nodes: List[FlowNode]) -> None:
        """Configure parameters for components.

        Args:
            component_requirements: The component requirements.
            nodes: The nodes in the flow.
        """
        # For each component requirement
        for i, requirement in enumerate(component_requirements):
            if i >= len(nodes):
                continue

            node = nodes[i]

            # Get parameters from requirement
            parameters = requirement.parameters

            # Update node template with parameters
            template = node.data["node"]["template"]

            for param_name, param_value in parameters.items():
                if param_name in template:
                    # Update the parameter value
                    if isinstance(template[param_name], dict) and "value" in template[param_name]:
                        template[param_name]["value"] = param_value
                    else:
                        template[param_name] = param_value

            # Handle API keys - set load_from_db to true for API key fields
            for param_name, param_info in template.items():
                if isinstance(param_info, dict):
                    # Check if this is an API key field
                    is_api_key = (
                        (param_name == "api_key" or param_name.endswith("_api_key")) and
                        "password" in param_info and param_info["password"]
                    )

                    # Also check if the field name contains "api_key" or if the display name contains "API Key"
                    if not is_api_key and "name" in param_info and "display_name" in param_info:
                        name_check = "api_key" in param_info["name"].lower()
                        display_name_check = "api key" in param_info["display_name"].lower()
                        is_api_key = is_api_key or name_check or display_name_check

                    if is_api_key:
                        # Set load_from_db to true to load from database
                        param_info["load_from_db"] = True

                        # If the value is a placeholder like "OPENAI_API_KEY", make sure it's not set to "dummy"
                        if "value" in param_info and isinstance(param_info["value"], str):
                            # Check if it's an environment variable name (all uppercase with underscores)
                            is_env_var = param_info["value"].upper() == param_info["value"] and "_" in param_info["value"]

                            if is_env_var:
                                # Try to get the actual API key
                                try:
                                    # This will raise an exception if the key is not found or is "dummy"
                                    api_key = await self._get_api_key(param_info["value"])

                                    # If we get here, we have a valid API key
                                    param_info["value"] = api_key
                                    logger.info(f"Set actual API key for {param_name}")
                                except ValueError as e:
                                    # This is expected if the key is not found or is "dummy"
                                    # We'll keep the placeholder name (e.g., "OPENAI_API_KEY") and ensure load_from_db is true
                                    logger.warning(f"API key not available for {param_name}: {str(e)}")
                                    logger.info(f"Using placeholder for {param_name} with load_from_db=true")
                                except Exception as e:
                                    # For other unexpected errors
                                    logger.error(f"Unexpected error getting API key for {param_name}: {str(e)}")
                                    logger.info(f"Using placeholder for {param_name} with load_from_db=true")

    async def _position_nodes(self, nodes: List[FlowNode]) -> None:
        """Position nodes in a visually appealing layout.

        Args:
            nodes: The nodes in the flow.
        """
        # Simple grid layout
        grid_size = max(int(len(nodes) ** 0.5), 1)
        node_width = 200
        node_height = 100
        margin = 50

        for i, node in enumerate(nodes):
            row = i // grid_size
            col = i % grid_size

            node.position = {
                "x": col * (node_width + margin),
                "y": row * (node_height + margin)
            }
