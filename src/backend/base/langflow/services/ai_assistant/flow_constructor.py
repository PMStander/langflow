"""Flow Constructor for the AI Assistant.

This module provides the FlowConstructor class that builds flows based on parsed instructions.
"""

from __future__ import annotations

import asyncio
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
        
        except Exception as e:
            logger.error(f"Error building flow: {str(e)}")
            # Return an empty flow
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
