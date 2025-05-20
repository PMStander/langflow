"""Component Knowledge Base for the AI Assistant.

This module provides the ComponentKnowledgeBase class that extracts and manages
metadata about all available components in Langflow.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
import json
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from langflow.services.settings.service import SettingsService


class ComponentKnowledgeBase:
    """Knowledge base for Langflow components.
    
    This class extracts and manages metadata about all available components,
    their inputs, outputs, and valid connections.
    """
    
    def __init__(self):
        """Initialize the ComponentKnowledgeBase."""
        # Dictionary of all components indexed by type and name
        self.components: Dict[str, Dict[str, Dict[str, Any]]] = {}
        
        # Graph representation of valid component connections
        # {source_component: {target_component: {source_field: target_field}}}
        self.connection_graph: Dict[str, Dict[str, Dict[str, str]]] = {}
        
        # Mapping of natural language concepts to component types and names
        self.semantic_mappings: Dict[str, List[Tuple[str, str]]] = {}
        
        # Component categories
        self.categories: Dict[str, List[str]] = {}
        
        # Input/output type compatibility
        self.type_compatibility: Dict[str, List[str]] = {}
        
        # Common component combinations
        self.common_combinations: List[Dict[str, Any]] = []
        
        # Component purpose classification
        self.purpose_classification: Dict[str, Dict[str, str]] = {}
        
    async def build_from_registry(self, settings_service) -> None:
        """Build the component knowledge base from the component registry.
        
        Args:
            settings_service: The settings service for accessing component paths.
        """
        logger.info("Building component knowledge base from registry")
        
        # Import here to avoid circular imports
        from langflow.interface.components import get_and_cache_all_types_dict
        
        # Get all component types
        all_types_dict = await get_and_cache_all_types_dict(settings_service)
        
        if not all_types_dict or "components" not in all_types_dict:
            logger.warning("No components found in registry")
            return
        
        # Store components
        self.components = all_types_dict["components"]
        
        # Extract component categories
        self.categories = {category: list(components.keys()) 
                          for category, components in self.components.items()}
        
        logger.info(f"Extracted metadata for {sum(len(comps) for comps in self.components.values())} components "
                   f"across {len(self.components)} categories")
    
    async def analyze_connection_compatibility(self) -> None:
        """Analyze component connection compatibility.
        
        This method builds a graph representation of valid component connections
        based on input/output type compatibility.
        """
        logger.info("Analyzing component connection compatibility")
        
        # Initialize connection graph
        self.connection_graph = defaultdict(lambda: defaultdict(dict))
        
        # Initialize type compatibility
        self.type_compatibility = defaultdict(list)
        
        # For each component category
        for category, components in self.components.items():
            # For each component in the category
            for comp_name, comp_data in components.items():
                source_id = f"{category}.{comp_name}"
                
                # Skip if no template or no outputs
                if "template" not in comp_data:
                    continue
                
                template = comp_data["template"]
                
                # Extract output types
                output_types = template.get("output_types", [])
                if not output_types and "output_type" in template:
                    output_types = [template["output_type"]]
                
                # For each output type, find compatible input types
                for output_type in output_types:
                    # For each potential target component category
                    for target_category, target_components in self.components.items():
                        # For each potential target component
                        for target_name, target_data in target_components.items():
                            target_id = f"{target_category}.{target_name}"
                            
                            # Skip self-connections
                            if source_id == target_id:
                                continue
                            
                            # Skip if no template
                            if "template" not in target_data:
                                continue
                            
                            target_template = target_data["template"]
                            
                            # Check if target accepts this output type
                            if self._is_compatible(output_type, target_template):
                                # Find compatible fields
                                compatible_fields = self._find_compatible_fields(
                                    output_type, target_template)
                                
                                # Add to connection graph
                                for source_field, target_field in compatible_fields:
                                    self.connection_graph[source_id][target_id][source_field] = target_field
                                
                                # Add to type compatibility
                                if output_type not in self.type_compatibility:
                                    self.type_compatibility[output_type] = []
                                
                                for input_type in self._get_input_types(target_template):
                                    if input_type not in self.type_compatibility[output_type]:
                                        self.type_compatibility[output_type].append(input_type)
        
        logger.info(f"Built connection graph with {len(self.connection_graph)} source components")
    
    def _is_compatible(self, output_type: str, target_template: Dict[str, Any]) -> bool:
        """Check if an output type is compatible with a target component.
        
        Args:
            output_type: The output type to check.
            target_template: The template of the target component.
            
        Returns:
            True if the output type is compatible with the target component.
        """
        # Check if target accepts this output type
        if "input_types" in target_template:
            return output_type in target_template["input_types"]
        
        # Check individual fields
        for field_name, field_info in target_template.get("inputs", {}).items():
            if isinstance(field_info, dict) and field_info.get("type") == output_type:
                return True
        
        return False
    
    def _find_compatible_fields(self, output_type: str, 
                               target_template: Dict[str, Any]) -> List[Tuple[str, str]]:
        """Find compatible fields between an output type and a target component.
        
        Args:
            output_type: The output type to check.
            target_template: The template of the target component.
            
        Returns:
            A list of tuples (source_field, target_field) of compatible fields.
        """
        compatible_fields = []
        
        # Default output field is 'output'
        source_field = "output"
        
        # Check individual input fields
        for field_name, field_info in target_template.get("inputs", {}).items():
            if isinstance(field_info, dict) and field_info.get("type") == output_type:
                compatible_fields.append((source_field, field_name))
        
        return compatible_fields
    
    def _get_input_types(self, template: Dict[str, Any]) -> List[str]:
        """Get all input types accepted by a component.
        
        Args:
            template: The component template.
            
        Returns:
            A list of input types.
        """
        input_types = []
        
        # Check if input_types is explicitly defined
        if "input_types" in template:
            return template["input_types"]
        
        # Check individual fields
        for field_name, field_info in template.get("inputs", {}).items():
            if isinstance(field_info, dict) and "type" in field_info:
                input_types.append(field_info["type"])
        
        return input_types
    
    async def create_semantic_mappings(self) -> None:
        """Create semantic mappings between natural language concepts and components.
        
        This method maps natural language concepts to component types and names.
        """
        logger.info("Creating semantic mappings")
        
        # Initialize semantic mappings
        self.semantic_mappings = defaultdict(list)
        
        # Initialize purpose classification
        self.purpose_classification = {}
        
        # For each component category
        for category, components in self.components.items():
            self.purpose_classification[category] = {}
            
            # For each component in the category
            for comp_name, comp_data in components.items():
                # Skip if no template
                if "template" not in comp_data:
                    continue
                
                template = comp_data["template"]
                
                # Get component display name
                display_name = comp_data.get("display_name", comp_name)
                
                # Get component description
                description = comp_data.get("description", "")
                
                # Add to semantic mappings
                self._add_to_semantic_mappings(category, comp_name, display_name, description)
                
                # Classify component purpose
                self._classify_component_purpose(category, comp_name, display_name, description)
        
        logger.info(f"Created semantic mappings with {len(self.semantic_mappings)} concepts")
    
    def _add_to_semantic_mappings(self, category: str, comp_name: str, 
                                 display_name: str, description: str) -> None:
        """Add a component to the semantic mappings.
        
        Args:
            category: The component category.
            comp_name: The component name.
            display_name: The component display name.
            description: The component description.
        """
        # Add category as a concept
        self.semantic_mappings[category.lower()].append((category, comp_name))
        
        # Add display name as a concept
        for word in display_name.lower().split():
            self.semantic_mappings[word].append((category, comp_name))
        
        # Add description keywords as concepts
        # This is a simple approach - in a real implementation, we would use NLP
        # to extract key concepts from the description
        for word in description.lower().split():
            if len(word) > 3:  # Skip short words
                self.semantic_mappings[word].append((category, comp_name))
    
    def _classify_component_purpose(self, category: str, comp_name: str,
                                  display_name: str, description: str) -> None:
        """Classify the purpose of a component.
        
        Args:
            category: The component category.
            comp_name: The component name.
            display_name: The component display name.
            description: The component description.
        """
        # This is a simple classification based on category
        # In a real implementation, we would use more sophisticated classification
        purpose = "unknown"
        
        # Classify based on category
        if category.lower() in ["llms", "chat_models"]:
            purpose = "language_model"
        elif category.lower() in ["prompts"]:
            purpose = "prompt"
        elif category.lower() in ["chains"]:
            purpose = "chain"
        elif category.lower() in ["agents"]:
            purpose = "agent"
        elif category.lower() in ["tools"]:
            purpose = "tool"
        elif category.lower() in ["memories"]:
            purpose = "memory"
        elif category.lower() in ["embeddings"]:
            purpose = "embedding"
        elif category.lower() in ["vectorstores"]:
            purpose = "vector_store"
        elif category.lower() in ["documentloaders"]:
            purpose = "document_loader"
        elif category.lower() in ["textsplitters"]:
            purpose = "text_splitter"
        elif category.lower() in ["retrievers"]:
            purpose = "retriever"
        elif category.lower() in ["outputs"]:
            purpose = "output"
        elif category.lower() in ["inputs"]:
            purpose = "input"
        
        self.purpose_classification[category][comp_name] = purpose
    
    async def get_component_info(self, component_type: str, component_name: str) -> Dict[str, Any]:
        """Get information about a specific component.
        
        Args:
            component_type: The type of the component.
            component_name: The name of the component.
            
        Returns:
            A dictionary containing information about the component.
        """
        if component_type not in self.components or component_name not in self.components[component_type]:
            return {}
        
        return self.components[component_type][component_name]
    
    async def get_compatible_components(self, component_type: str, component_name: str) -> List[Dict[str, Any]]:
        """Get a list of components that are compatible with the specified component.
        
        Args:
            component_type: The type of the component.
            component_name: The name of the component.
            
        Returns:
            A list of dictionaries containing information about compatible components.
        """
        source_id = f"{component_type}.{component_name}"
        
        if source_id not in self.connection_graph:
            return []
        
        compatible_components = []
        
        for target_id, field_mappings in self.connection_graph[source_id].items():
            target_type, target_name = target_id.split(".", 1)
            
            if target_type in self.components and target_name in self.components[target_type]:
                component_info = self.components[target_type][target_name].copy()
                component_info["field_mappings"] = field_mappings
                compatible_components.append(component_info)
        
        return compatible_components
