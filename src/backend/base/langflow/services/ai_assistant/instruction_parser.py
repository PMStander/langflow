"""Instruction Parser for the AI Assistant.

This module provides the InstructionParser class that interprets natural language instructions
and extracts key requirements for flow construction.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from loguru import logger
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from langflow.services.ai_assistant.knowledge_base import ComponentKnowledgeBase
    from langflow.services.settings.service import SettingsService


class ComponentRequirement(BaseModel):
    """A requirement for a component in a flow.

    This class represents a component that should be included in a flow,
    along with its configuration parameters.
    """

    component_type: str = Field(..., description="The type of the component (e.g., 'llms', 'chains')")
    component_name: str = Field(..., description="The name of the component (e.g., 'openai', 'llm_chain')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters for the component")
    description: str = Field("", description="A description of what this component does in the flow")


class ConnectionRequirement(BaseModel):
    """A requirement for a connection between components in a flow.

    This class represents a connection that should be created between two components
    in a flow, specifying the source and target components and fields.
    """

    source_component_idx: int = Field(..., description="The index of the source component in the components list")
    target_component_idx: int = Field(..., description="The index of the target component in the components list")
    source_field: str = Field("output", description="The output field of the source component")
    target_field: str = Field(..., description="The input field of the target component")
    description: str = Field("", description="A description of what this connection represents")


class ClarificationQuestion(BaseModel):
    """A question to ask the user for clarification.

    This class represents a question that should be asked to the user to clarify
    ambiguous or incomplete instructions.
    """

    question_id: str = Field(..., description="A unique identifier for the question")
    question: str = Field(..., description="The question to ask the user")
    options: List[str] = Field(default_factory=list, description="Possible options for the answer")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context information for the question")


class ParsedInstruction(BaseModel):
    """The result of parsing a natural language instruction.

    This class contains the extracted components, connections, and any clarification
    questions that need to be asked.
    """

    instruction: str = Field(..., description="The original instruction")
    components: List[ComponentRequirement] = Field(default_factory=list, description="Required components")
    connections: List[ConnectionRequirement] = Field(default_factory=list, description="Required connections")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Global parameters")
    clarification_needed: bool = Field(False, description="Whether clarification is needed")
    clarification_questions: List[ClarificationQuestion] = Field(default_factory=list, description="Questions to ask")
    flow_description: str = Field("", description="A description of what the flow does")


class InstructionParser:
    """Parser for natural language instructions.

    This class interprets natural language instructions and extracts key requirements
    for flow construction, including components, connections, and parameters.
    """

    def __init__(self, knowledge_base: ComponentKnowledgeBase, settings_service: SettingsService):
        """Initialize the InstructionParser.

        Args:
            knowledge_base: The component knowledge base.
            settings_service: The settings service for accessing LLM configurations.
        """
        self.knowledge_base = knowledge_base
        self.settings_service = settings_service
        self.llm_provider = None
        self.llm_model = None

    async def set_llm_provider(self, provider_name: str, model_name: str) -> None:
        """Set the LLM provider and model to use for instruction parsing.

        Args:
            provider_name: The name of the LLM provider (e.g., 'OpenAI', 'Anthropic').
            model_name: The name of the model to use.
        """
        self.llm_provider = provider_name
        self.llm_model = model_name

    async def parse_instruction(self, instruction: str) -> ParsedInstruction:
        """Parse a natural language instruction.

        Args:
            instruction: The natural language instruction to parse.

        Returns:
            A ParsedInstruction object containing the extracted components, connections,
            and any clarification questions.
        """
        logger.info(f"Parsing instruction: {instruction}")

        try:
            # Get the LLM response
            llm_response = await self._get_llm_response(instruction)

            # Parse the LLM response
            parsed_instruction = await self._parse_llm_response(instruction, llm_response)

            # Validate the parsed instruction
            parsed_instruction = await self._validate_parsed_instruction(parsed_instruction)

            return parsed_instruction

        except Exception as e:
            logger.error(f"Error parsing instruction: {str(e)}")
            # Return a basic parsed instruction with an error message
            return ParsedInstruction(
                instruction=instruction,
                clarification_needed=True,
                clarification_questions=[
                    ClarificationQuestion(
                        question_id="error",
                        question=f"I encountered an error while parsing your instruction: {str(e)}. Could you please rephrase or provide more details?",
                    )
                ],
            )

    async def _get_llm_response(self, instruction: str) -> str:
        """Get a response from the LLM for the given instruction.

        Args:
            instruction: The natural language instruction.

        Returns:
            The LLM response as a string.
        """
        # Use the configured LLM provider and model
        provider = self.llm_provider or "OpenAI"
        model = self.llm_model or "gpt-4"

        # Get the prompt for instruction parsing
        prompt = self._get_instruction_parsing_prompt(instruction)

        # Call the appropriate LLM based on the provider
        if provider.lower() == "openai":
            return await self._call_openai(prompt, model)
        elif provider.lower() == "anthropic":
            return await self._call_anthropic(prompt, model)
        else:
            # Default to OpenAI
            logger.warning(f"Unsupported LLM provider: {provider}. Falling back to OpenAI.")
            return await self._call_openai(prompt, model)

    async def _call_openai(self, prompt: str, model: str) -> str:
        """Call the OpenAI API to get a response.

        Args:
            prompt: The prompt to send to the API.
            model: The model to use.

        Returns:
            The API response as a string.
        """
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, SystemMessage

            # Get API key from settings
            api_key = await self._get_api_key("OPENAI_API_KEY")

            # Create the ChatOpenAI instance
            chat = ChatOpenAI(
                model=model,
                temperature=0.2,
                api_key=api_key,
            )

            # Create the messages
            messages = [
                SystemMessage(content="You are an AI assistant that helps users build LangChain flows. Your task is to interpret natural language instructions and extract the components, connections, and parameters needed to build a flow."),
                HumanMessage(content=prompt),
            ]

            # Get the response
            response = chat.invoke(messages)

            return response.content

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

    async def _call_anthropic(self, prompt: str, model: str) -> str:
        """Call the Anthropic API to get a response.

        Args:
            prompt: The prompt to send to the API.
            model: The model to use.

        Returns:
            The API response as a string.
        """
        try:
            from langchain_anthropic import ChatAnthropic
            from langchain_core.messages import HumanMessage, SystemMessage

            # Get API key from settings
            api_key = await self._get_api_key("ANTHROPIC_API_KEY")

            # Create the ChatAnthropic instance
            chat = ChatAnthropic(
                model=model,
                temperature=0.2,
                anthropic_api_key=api_key,
            )

            # Create the messages
            messages = [
                SystemMessage(content="You are an AI assistant that helps users build LangChain flows. Your task is to interpret natural language instructions and extract the components, connections, and parameters needed to build a flow."),
                HumanMessage(content=prompt),
            ]

            # Get the response
            response = chat.invoke(messages)

            return response.content

        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            raise

    async def _get_api_key(self, key_name: str) -> str:
        """Get an API key from the settings.

        Args:
            key_name: The name of the API key to get.

        Returns:
            The API key as a string.
        """
        import os
        from uuid import UUID
        from sqlalchemy.ext.asyncio import AsyncSession

        # Initialize api_key to None at the beginning
        api_key = None

        # First try to get the API key from environment variables
        api_key = os.environ.get(key_name)
        if api_key:
            logger.info(f"Found {key_name} in environment variables")

        # If not found in environment variables, try to get it from the variable service
        if not api_key:
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
                            api_key = await variable_service.get_variable(
                                user_id=user.id,
                                name=key_name,
                                field=key_name.lower(),
                                session=session
                            )
                            logger.info(f"Successfully retrieved {key_name} from variable service")
                            logger.debug(f"Value retrieved from variable service for {key_name}: {api_key}") # Add this debug log
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

    def _get_instruction_parsing_prompt(self, instruction: str) -> str:
        """Get the prompt for instruction parsing.

        Args:
            instruction: The natural language instruction.

        Returns:
            The prompt as a string.
        """
        # Get the available component types and names
        component_info = self._get_component_info()

        # Create the prompt
        prompt = f"""
I want you to help me build a LangChain flow based on the following instruction:

"{instruction}"

Based on this instruction, please identify the components, connections, and parameters needed to build the flow.

Available component types and names:
{component_info}

Please respond with a JSON object that includes the following:
1. "components": A list of components needed, each with "component_type", "component_name", "parameters", and "description"
2. "connections": A list of connections between components, each with "source_component_idx", "target_component_idx", "source_field", "target_field", and "description"
3. "parameters": Any global parameters for the flow
4. "clarification_needed": A boolean indicating whether clarification is needed
5. "clarification_questions": A list of questions to ask if clarification is needed, each with "question_id", "question", and optionally "options"
6. "flow_description": A brief description of what the flow does

Only respond with the JSON object, no additional text.
"""

        return prompt

    def _get_component_info(self) -> str:
        """Get information about available components.

        Returns:
            A string containing information about available component types and names.
        """
        component_info = []

        # Add information for each component category
        for category, components in self.knowledge_base.components.items():
            component_names = list(components.keys())
            component_info.append(f"- {category}: {', '.join(component_names)}")

        return "\n".join(component_info)

    async def _parse_llm_response(self, instruction: str, llm_response: str) -> ParsedInstruction:
        """Parse the LLM response into a ParsedInstruction object.

        Args:
            instruction: The original instruction.
            llm_response: The response from the LLM.

        Returns:
            A ParsedInstruction object.
        """
        try:
            # Extract the JSON object from the response
            json_str = llm_response.strip()

            # If the response is wrapped in ```json and ```, extract the JSON
            if json_str.startswith("```json"):
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif json_str.startswith("```"):
                json_str = json_str.split("```")[1].split("```")[0].strip()

            # Parse the JSON
            data = json.loads(json_str)

            # Create the ParsedInstruction object
            parsed_instruction = ParsedInstruction(
                instruction=instruction,
                components=[ComponentRequirement(**comp) for comp in data.get("components", [])],
                connections=[ConnectionRequirement(**conn) for conn in data.get("connections", [])],
                parameters=data.get("parameters", {}),
                clarification_needed=data.get("clarification_needed", False),
                clarification_questions=[ClarificationQuestion(**q) for q in data.get("clarification_questions", [])],
                flow_description=data.get("flow_description", ""),
            )

            return parsed_instruction

        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            logger.debug(f"LLM response: {llm_response}")
            raise

    async def _validate_parsed_instruction(self, parsed_instruction: ParsedInstruction) -> ParsedInstruction:
        """Validate the parsed instruction and add any necessary clarification questions.

        Args:
            parsed_instruction: The parsed instruction to validate.

        Returns:
            The validated parsed instruction.
        """
        # Check if components exist
        for i, component in enumerate(parsed_instruction.components):
            component_type = component.component_type
            component_name = component.component_name

            # Check if the component type exists
            if component_type not in self.knowledge_base.components:
                parsed_instruction.clarification_needed = True
                parsed_instruction.clarification_questions.append(
                    ClarificationQuestion(
                        question_id=f"invalid_component_type_{i}",
                        question=f"The component type '{component_type}' does not exist. Did you mean one of these: {', '.join(self.knowledge_base.categories.keys())}?",
                        options=list(self.knowledge_base.categories.keys()),
                        context={"component_idx": i},
                    )
                )
                continue

            # Check if the component name exists
            if component_name not in self.knowledge_base.components[component_type]:
                parsed_instruction.clarification_needed = True
                parsed_instruction.clarification_questions.append(
                    ClarificationQuestion(
                        question_id=f"invalid_component_name_{i}",
                        question=f"The component name '{component_name}' does not exist in the '{component_type}' category. Did you mean one of these: {', '.join(self.knowledge_base.components[component_type].keys())}?",
                        options=list(self.knowledge_base.components[component_type].keys()),
                        context={"component_idx": i, "component_type": component_type},
                    )
                )

        # Check if connections are valid
        for i, connection in enumerate(parsed_instruction.connections):
            source_idx = connection.source_component_idx
            target_idx = connection.target_component_idx

            # Check if the indices are valid
            if source_idx < 0 or source_idx >= len(parsed_instruction.components):
                parsed_instruction.clarification_needed = True
                parsed_instruction.clarification_questions.append(
                    ClarificationQuestion(
                        question_id=f"invalid_source_idx_{i}",
                        question=f"The source component index {source_idx} is invalid. Please provide a valid index between 0 and {len(parsed_instruction.components) - 1}.",
                        context={"connection_idx": i},
                    )
                )
                continue

            if target_idx < 0 or target_idx >= len(parsed_instruction.components):
                parsed_instruction.clarification_needed = True
                parsed_instruction.clarification_questions.append(
                    ClarificationQuestion(
                        question_id=f"invalid_target_idx_{i}",
                        question=f"The target component index {target_idx} is invalid. Please provide a valid index between 0 and {len(parsed_instruction.components) - 1}.",
                        context={"connection_idx": i},
                    )
                )
                continue

            # Get the source and target components
            source_component = parsed_instruction.components[source_idx]
            target_component = parsed_instruction.components[target_idx]

            # Check if the connection is valid
            source_id = f"{source_component.component_type}.{source_component.component_name}"
            target_id = f"{target_component.component_type}.{target_component.component_name}"

            if source_id not in self.knowledge_base.connection_graph or target_id not in self.knowledge_base.connection_graph[source_id]:
                parsed_instruction.clarification_needed = True
                parsed_instruction.clarification_questions.append(
                    ClarificationQuestion(
                        question_id=f"invalid_connection_{i}",
                        question=f"The connection from '{source_id}' to '{target_id}' is not valid. These components cannot be directly connected.",
                        context={"connection_idx": i},
                    )
                )

        return parsed_instruction
