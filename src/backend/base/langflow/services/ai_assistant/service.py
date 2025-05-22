"""AI Assistant Service for Langflow.

This module provides the AI Assistant Service that helps users build flows through natural language instructions.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from loguru import logger

from langflow.services.base import Service
from langflow.services.ai_assistant.knowledge_base import ComponentKnowledgeBase
from langflow.services.ai_assistant.instruction_parser import InstructionParser, ParsedInstruction
from langflow.services.ai_assistant.flow_constructor import FlowConstructor

if TYPE_CHECKING:
    from langflow.services.settings.service import SettingsService


class AIAssistantService(Service):
    """Service for the AI Flow Builder Assistant.

    This service provides functionality to interpret natural language instructions
    and build flows by selecting and connecting appropriate components.
    """

    name = "ai_assistant_service"

    def __init__(self, settings_service: SettingsService):
        """Initialize the AI Assistant Service.

        Args:
            settings_service: The settings service for accessing application settings.
        """
        self.settings_service = settings_service
        self.knowledge_base = ComponentKnowledgeBase()
        self.instruction_parser = None
        self.flow_constructor = None
        self.llm_provider = "OpenAI"  # Default LLM provider
        self.llm_model = "gpt-4"  # Default LLM model
        self.initialized = False
        self.ready = False

    async def initialize(self) -> None:
        """Initialize the AI Assistant Service.

        This method builds the component knowledge base by extracting metadata
        from all registered components and analyzing their relationships.
        """
        if self.initialized:
            return

        logger.info("Initializing AI Assistant Service")
        try:
            # Build the component knowledge base
            await self.knowledge_base.build_from_registry(self.settings_service)

            # Check if components were loaded
            if not self.knowledge_base.components:
                logger.warning("No components were loaded in the knowledge base")
                # We'll continue anyway since we've added fallback components
            else:
                logger.info(f"Successfully loaded {sum(len(comps) for comps in self.knowledge_base.components.values())} components")

            # Analyze component relationships
            await self.knowledge_base.analyze_connection_compatibility()

            # Create semantic mappings
            await self.knowledge_base.create_semantic_mappings()

            # Initialize the instruction parser
            self.instruction_parser = InstructionParser(self.knowledge_base, self.settings_service)
            await self.instruction_parser.set_llm_provider(self.llm_provider, self.llm_model)

            # Initialize the flow constructor
            self.flow_constructor = FlowConstructor(self.knowledge_base)

            self.initialized = True
            self.ready = True
            logger.info("AI Assistant Service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI Assistant Service: {str(e)}")
            # Log more details about the error
            logger.exception("Detailed error information:")
            raise

    async def set_llm_provider(self, provider_name: str, model_name: str) -> None:
        """Set the LLM provider and model to use for instruction parsing.

        Args:
            provider_name: The name of the LLM provider (e.g., 'OpenAI', 'Anthropic').
            model_name: The name of the model to use.
        """
        self.llm_provider = provider_name
        self.llm_model = model_name

        if self.instruction_parser:
            await self.instruction_parser.set_llm_provider(provider_name, model_name)

    async def interpret_instruction(self, instruction: str) -> Dict[str, Any]:
        """Interpret a natural language instruction.

        Args:
            instruction: The natural language instruction to interpret.

        Returns:
            A dictionary containing the interpreted instruction details.
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Parse the instruction using the instruction parser
            parsed_instruction = await self.instruction_parser.parse_instruction(instruction)

            # Convert the parsed instruction to a dictionary
            return parsed_instruction.model_dump()

        except Exception as e:
            logger.error(f"Error interpreting instruction: {str(e)}")
            # Return a basic response with an error message
            return {
                "instruction": instruction,
                "components": [],
                "connections": [],
                "parameters": {},
                "clarification_needed": True,
                "clarification_questions": [
                    {
                        "question_id": "error",
                        "question": f"I encountered an error while interpreting your instruction: {str(e)}. Could you please rephrase or provide more details?",
                        "options": [],
                        "context": {}
                    }
                ],
                "flow_description": ""
            }

    async def build_flow_from_instruction(self, instruction: str) -> Dict[str, Any]:
        """Build a flow from a natural language instruction.

        Args:
            instruction: The natural language instruction to build a flow from.

        Returns:
            A dictionary containing the flow data.
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Interpret the instruction
            interpretation_dict = await self.interpret_instruction(instruction)

            # Check if clarification is needed
            if interpretation_dict.get("clarification_needed", False):
                # Return the interpretation without building a flow
                return {
                    "instruction": instruction,
                    "interpretation": interpretation_dict,
                    "flow": {
                        "nodes": [],
                        "edges": []
                    }
                }

            # Convert the interpretation dictionary back to a ParsedInstruction object
            parsed_instruction = ParsedInstruction(**interpretation_dict)

            # Build the flow using the flow constructor
            flow = await self.flow_constructor.build_flow(parsed_instruction)

            # Return the flow data
            return {
                "instruction": instruction,
                "interpretation": interpretation_dict,
                "flow": {
                    "nodes": [node.model_dump() for node in flow.nodes],
                    "edges": [edge.model_dump() for edge in flow.edges]
                }
            }
        except Exception as e:
            logger.error(f"Error building flow from instruction: {str(e)}")
            # Return a basic response with an error message
            return {
                "instruction": instruction,
                "interpretation": {
                    "instruction": instruction,
                    "components": [],
                    "connections": [],
                    "parameters": {},
                    "clarification_needed": True,
                    "clarification_questions": [
                        {
                            "question_id": "error",
                            "question": f"I encountered an error while building the flow: {str(e)}. Could you please rephrase or provide more details?",
                            "options": [],
                            "context": {}
                        }
                    ],
                    "flow_description": ""
                },
                "flow": {
                    "nodes": [],
                    "edges": []
                }
            }

    async def process_clarification_response(self, question_id: str, response: str) -> Dict[str, Any]:
        """Process a response to a clarification question.

        Args:
            question_id: The ID of the question being answered.
            response: The user's response to the question.

        Returns:
            An updated interpretation dictionary.
        """
        if not self.initialized:
            await self.initialize()

        # TODO: Implement clarification response processing
        # This is a placeholder for now - will be implemented in the next phase
        return {
            "question_id": question_id,
            "response": response,
            "processed": True,
            "updated_interpretation": {
                "components": [],
                "connections": [],
                "parameters": {},
                "clarification_needed": False,
                "clarification_questions": []
            }
        }

    async def get_component_info(self, component_type: str, component_name: str) -> Dict[str, Any]:
        """Get information about a specific component.

        Args:
            component_type: The type of the component.
            component_name: The name of the component.

        Returns:
            A dictionary containing information about the component.
        """
        if not self.initialized:
            await self.initialize()

        return await self.knowledge_base.get_component_info(component_type, component_name)

    async def get_compatible_components(self, component_type: str, component_name: str) -> List[Dict[str, Any]]:
        """Get a list of components that are compatible with the specified component.

        Args:
            component_type: The type of the component.
            component_name: The name of the component.

        Returns:
            A list of dictionaries containing information about compatible components.
        """
        if not self.initialized:
            await self.initialize()

        return await self.knowledge_base.get_compatible_components(component_type, component_name)

    async def get_available_llm_providers(self) -> Dict[str, List[str]]:
        """Get a list of available LLM providers and models.

        Returns:
            A dictionary mapping provider names to lists of model names.
        """
        if not self.initialized:
            await self.initialize()

        # Get all LLM providers from the component registry
        llm_providers = {}

        # Get language model components from the knowledge base
        language_model_components = self.knowledge_base.get_components_by_type("LLM")

        for component in language_model_components:
            # Extract provider information from component metadata
            if hasattr(component, "inputs"):
                provider_input = next((inp for inp in component.inputs if inp.name == "provider"), None)
                if provider_input and hasattr(provider_input, "options"):
                    for provider in provider_input.options:
                        if provider not in llm_providers:
                            # Find the corresponding model input for this provider
                            model_input = next((inp for inp in component.inputs if inp.name == "model_name"), None)
                            if model_input and hasattr(model_input, "options"):
                                llm_providers[provider] = model_input.options

        # If no providers were found, fall back to defaults
        if not llm_providers:
            llm_providers = {
                "OpenAI": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                "Anthropic": ["claude-2", "claude-instant-1", "claude-3-opus", "claude-3-sonnet"],
            }

        return llm_providers

    async def refresh_knowledge_base(self) -> None:
        """Refresh the component knowledge base.

        This method rebuilds the knowledge base from the component registry,
        ensuring that all components (including those from bundles) are available.
        """
        logger.info("Refreshing AI Assistant knowledge base")
        try:
            # Import here to avoid circular imports
            from langflow.interface.components import get_and_cache_all_types_dict, aget_all_types_dict

            # Reset initialization flag to force rebuild
            self.initialized = False
            self.ready = False

            # Clear the existing knowledge base
            self.knowledge_base = ComponentKnowledgeBase()

            # Force reload all components including bundles
            # First clear the cache to ensure we get fresh data
            from langflow.interface.components import component_cache
            component_cache.all_types_dict = None
            component_cache.fully_loaded_components = {}

            # Get all component types with fresh data
            all_types_dict = await get_and_cache_all_types_dict(self.settings_service)

            # If still no components, try direct loading
            if not all_types_dict or "components" not in all_types_dict or not all_types_dict["components"]:
                logger.warning("No components found in registry after refresh, attempting direct load")
                all_types_dict = await aget_all_types_dict(self.settings_service.settings.components_path)

            # Log component count for debugging
            if all_types_dict and "components" in all_types_dict:
                component_count = sum(len(comps) for comps in all_types_dict["components"].values())
                logger.info(f"Loaded {component_count} components during refresh")

                # Log available component types
                logger.info(f"Available component types: {list(all_types_dict['components'].keys())}")

                # Check for firecrawl components specifically
                for component_type, components in all_types_dict["components"].items():
                    firecrawl_components = [name for name in components.keys() if "firecrawl" in name.lower()]
                    if firecrawl_components:
                        logger.info(f"Found firecrawl components in {component_type}: {firecrawl_components}")

            # Rebuild the knowledge base
            await self.knowledge_base.build_from_registry(self.settings_service)

            # Analyze component relationships
            await self.knowledge_base.analyze_connection_compatibility()

            # Create semantic mappings
            await self.knowledge_base.create_semantic_mappings()

            # Initialize the instruction parser
            self.instruction_parser = InstructionParser(self.knowledge_base, self.settings_service)
            await self.instruction_parser.set_llm_provider(self.llm_provider, self.llm_model)

            # Initialize the flow constructor
            self.flow_constructor = FlowConstructor(self.knowledge_base)

            self.initialized = True
            self.ready = True
            logger.info("AI Assistant knowledge base refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing AI Assistant knowledge base: {str(e)}")
            logger.exception("Detailed error information:")
            raise

    async def teardown(self) -> None:
        """Clean up resources used by the AI Assistant Service."""
        logger.info("Tearing down AI Assistant Service")
        # No specific cleanup needed for now
        self.initialized = False
        self.ready = False
