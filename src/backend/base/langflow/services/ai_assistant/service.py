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
        # This is a simplified implementation - in a real implementation,
        # we would get this information from the settings service
        return {
            "OpenAI": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            "Anthropic": ["claude-2", "claude-instant-1", "claude-3-opus", "claude-3-sonnet"],
        }

    async def teardown(self) -> None:
        """Clean up resources used by the AI Assistant Service."""
        logger.info("Tearing down AI Assistant Service")
        # No specific cleanup needed for now
        self.initialized = False
        self.ready = False
