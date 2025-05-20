"""Tests for the AI Assistant Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langflow.services.ai_assistant.service import AIAssistantService
from langflow.services.ai_assistant.instruction_parser import ParsedInstruction


@pytest.fixture
def mock_settings_service():
    """Create a mock settings service."""
    settings_service = MagicMock()
    settings_service.settings.components_path = ["/path/to/components"]
    return settings_service


@pytest.fixture
def mock_instruction_parser():
    """Create a mock instruction parser."""
    parser = MagicMock()
    parser.parse_instruction = AsyncMock()
    parser.set_llm_provider = AsyncMock()
    return parser


@pytest.fixture
def ai_assistant_service(mock_settings_service):
    """Create an AIAssistantService instance."""
    service = AIAssistantService(mock_settings_service)
    service.knowledge_base = MagicMock()
    return service


@pytest.mark.asyncio
async def test_initialize(ai_assistant_service):
    """Test initializing the AI Assistant Service."""
    # Mock the knowledge base methods
    ai_assistant_service.knowledge_base.build_from_registry = AsyncMock()
    ai_assistant_service.knowledge_base.analyze_connection_compatibility = AsyncMock()
    ai_assistant_service.knowledge_base.create_semantic_mappings = AsyncMock()

    # Mock the instruction parser
    with patch("langflow.services.ai_assistant.instruction_parser.InstructionParser") as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser.set_llm_provider = AsyncMock()
        mock_parser_class.return_value = mock_parser

        # Initialize the service
        await ai_assistant_service.initialize()

        # Check that the knowledge base methods were called
        ai_assistant_service.knowledge_base.build_from_registry.assert_called_once_with(
            ai_assistant_service.settings_service)
        ai_assistant_service.knowledge_base.analyze_connection_compatibility.assert_called_once()
        ai_assistant_service.knowledge_base.create_semantic_mappings.assert_called_once()

        # Check that the instruction parser was created and initialized
        mock_parser_class.assert_called_once_with(ai_assistant_service.knowledge_base, ai_assistant_service.settings_service)
        mock_parser.set_llm_provider.assert_called_once_with(ai_assistant_service.llm_provider, ai_assistant_service.llm_model)

        # Check that the service is initialized and ready
        assert ai_assistant_service.initialized
        assert ai_assistant_service.ready


@pytest.mark.asyncio
async def test_set_llm_provider(ai_assistant_service):
    """Test setting the LLM provider and model."""
    # Mock the instruction parser
    ai_assistant_service.instruction_parser = MagicMock()
    ai_assistant_service.instruction_parser.set_llm_provider = AsyncMock()

    # Set the LLM provider and model
    await ai_assistant_service.set_llm_provider("OpenAI", "gpt-4")

    # Check that the provider and model were set
    assert ai_assistant_service.llm_provider == "OpenAI"
    assert ai_assistant_service.llm_model == "gpt-4"

    # Check that the instruction parser was updated
    ai_assistant_service.instruction_parser.set_llm_provider.assert_called_once_with("OpenAI", "gpt-4")


@pytest.mark.asyncio
async def test_interpret_instruction(ai_assistant_service, mock_instruction_parser):
    """Test interpreting a natural language instruction."""
    # Mock the initialize method
    ai_assistant_service.initialize = AsyncMock()
    ai_assistant_service.instruction_parser = mock_instruction_parser

    # Mock the parse_instruction method to return a ParsedInstruction
    parsed_instruction = ParsedInstruction(
        instruction="Create a chatbot using OpenAI",
        components=[],
        connections=[],
        parameters={},
        clarification_needed=False,
        clarification_questions=[],
        flow_description="A chatbot using OpenAI"
    )
    mock_instruction_parser.parse_instruction.return_value = parsed_instruction

    # Interpret an instruction
    result = await ai_assistant_service.interpret_instruction("Create a chatbot using OpenAI")

    # Check that initialize was called
    ai_assistant_service.initialize.assert_called_once()

    # Check that parse_instruction was called
    mock_instruction_parser.parse_instruction.assert_called_once_with("Create a chatbot using OpenAI")

    # Check the result structure
    assert "instruction" in result
    assert "components" in result
    assert "connections" in result
    assert "parameters" in result
    assert "clarification_needed" in result
    assert "clarification_questions" in result
    assert "flow_description" in result

    # Check that the instruction was stored
    assert result["instruction"] == "Create a chatbot using OpenAI"
    assert result["flow_description"] == "A chatbot using OpenAI"


@pytest.mark.asyncio
async def test_interpret_instruction_error(ai_assistant_service, mock_instruction_parser):
    """Test interpreting a natural language instruction with an error."""
    # Mock the initialize method
    ai_assistant_service.initialize = AsyncMock()
    ai_assistant_service.instruction_parser = mock_instruction_parser

    # Mock the parse_instruction method to raise an exception
    mock_instruction_parser.parse_instruction.side_effect = Exception("Test error")

    # Interpret an instruction
    result = await ai_assistant_service.interpret_instruction("Create a chatbot using OpenAI")

    # Check that initialize was called
    ai_assistant_service.initialize.assert_called_once()

    # Check that parse_instruction was called
    mock_instruction_parser.parse_instruction.assert_called_once_with("Create a chatbot using OpenAI")

    # Check the result structure
    assert "instruction" in result
    assert "components" in result
    assert "connections" in result
    assert "parameters" in result
    assert "clarification_needed" in result
    assert "clarification_questions" in result

    # Check that the error was handled
    assert result["instruction"] == "Create a chatbot using OpenAI"
    assert result["clarification_needed"] is True
    assert len(result["clarification_questions"]) == 1
    assert "error" in result["clarification_questions"][0]["question_id"]
    assert "Test error" in result["clarification_questions"][0]["question"]


@pytest.mark.asyncio
async def test_build_flow_from_instruction(ai_assistant_service):
    """Test building a flow from a natural language instruction."""
    # Mock the initialize and interpret_instruction methods
    ai_assistant_service.initialize = AsyncMock()
    ai_assistant_service.interpret_instruction = AsyncMock(return_value={
        "instruction": "Create a chatbot using OpenAI",
        "components": [],
        "connections": [],
        "parameters": {},
        "clarification_needed": False,
        "clarification_questions": [],
        "flow_description": "A chatbot using OpenAI"
    })

    # Build a flow from an instruction
    result = await ai_assistant_service.build_flow_from_instruction("Create a chatbot using OpenAI")

    # Check that initialize and interpret_instruction were called
    ai_assistant_service.initialize.assert_called_once()
    ai_assistant_service.interpret_instruction.assert_called_once_with(
        "Create a chatbot using OpenAI")

    # Check the result structure
    assert "instruction" in result
    assert "interpretation" in result
    assert "flow" in result

    # Check that the instruction was stored
    assert result["instruction"] == "Create a chatbot using OpenAI"
    assert "nodes" in result["flow"]
    assert "edges" in result["flow"]


@pytest.mark.asyncio
async def test_build_flow_with_clarification_needed(ai_assistant_service):
    """Test building a flow when clarification is needed."""
    # Mock the initialize and interpret_instruction methods
    ai_assistant_service.initialize = AsyncMock()
    ai_assistant_service.interpret_instruction = AsyncMock(return_value={
        "instruction": "Create a chatbot",
        "components": [],
        "connections": [],
        "parameters": {},
        "clarification_needed": True,
        "clarification_questions": [
            {
                "question_id": "llm_type",
                "question": "Which LLM would you like to use?",
                "options": ["OpenAI", "Anthropic"],
                "context": {}
            }
        ],
        "flow_description": "A chatbot"
    })

    # Build a flow from an instruction
    result = await ai_assistant_service.build_flow_from_instruction("Create a chatbot")

    # Check that initialize and interpret_instruction were called
    ai_assistant_service.initialize.assert_called_once()
    ai_assistant_service.interpret_instruction.assert_called_once_with(
        "Create a chatbot")

    # Check the result structure
    assert "instruction" in result
    assert "interpretation" in result
    assert "flow" in result

    # Check that the clarification questions were included
    assert result["interpretation"]["clarification_needed"] is True
    assert len(result["interpretation"]["clarification_questions"]) == 1
    assert result["interpretation"]["clarification_questions"][0]["question_id"] == "llm_type"

    # Check that the flow is empty
    assert result["flow"]["nodes"] == []
    assert result["flow"]["edges"] == []


@pytest.mark.asyncio
async def test_process_clarification_response(ai_assistant_service):
    """Test processing a clarification response."""
    # Mock the initialize method
    ai_assistant_service.initialize = AsyncMock()

    # Process a clarification response
    result = await ai_assistant_service.process_clarification_response("llm_type", "OpenAI")

    # Check that initialize was called
    ai_assistant_service.initialize.assert_called_once()

    # Check the result structure
    assert "question_id" in result
    assert "response" in result
    assert "processed" in result
    assert "updated_interpretation" in result

    # Check that the response was processed
    assert result["question_id"] == "llm_type"
    assert result["response"] == "OpenAI"
    assert result["processed"] is True


@pytest.mark.asyncio
async def test_get_component_info(ai_assistant_service):
    """Test getting component information."""
    # Mock the initialize method and knowledge_base.get_component_info
    ai_assistant_service.initialize = AsyncMock()
    ai_assistant_service.knowledge_base.get_component_info = AsyncMock(return_value={
        "display_name": "OpenAI",
        "description": "OpenAI language model",
    })

    # Get component info
    result = await ai_assistant_service.get_component_info("llms", "openai")

    # Check that initialize and get_component_info were called
    ai_assistant_service.initialize.assert_called_once()
    ai_assistant_service.knowledge_base.get_component_info.assert_called_once_with(
        "llms", "openai")

    # Check the result
    assert result["display_name"] == "OpenAI"
    assert result["description"] == "OpenAI language model"


@pytest.mark.asyncio
async def test_get_compatible_components(ai_assistant_service):
    """Test getting compatible components."""
    # Mock the initialize method and knowledge_base.get_compatible_components
    ai_assistant_service.initialize = AsyncMock()
    ai_assistant_service.knowledge_base.get_compatible_components = AsyncMock(return_value=[
        {
            "display_name": "LLM Chain",
            "description": "A chain that uses an LLM",
        }
    ])

    # Get compatible components
    result = await ai_assistant_service.get_compatible_components("llms", "openai")

    # Check that initialize and get_compatible_components were called
    ai_assistant_service.initialize.assert_called_once()
    ai_assistant_service.knowledge_base.get_compatible_components.assert_called_once_with(
        "llms", "openai")

    # Check the result
    assert len(result) == 1
    assert result[0]["display_name"] == "LLM Chain"
    assert result[0]["description"] == "A chain that uses an LLM"


@pytest.mark.asyncio
async def test_get_available_llm_providers(ai_assistant_service):
    """Test getting available LLM providers."""
    # Mock the initialize method
    ai_assistant_service.initialize = AsyncMock()

    # Get available LLM providers
    result = await ai_assistant_service.get_available_llm_providers()

    # Check that initialize was called
    ai_assistant_service.initialize.assert_called_once()

    # Check the result structure
    assert "OpenAI" in result
    assert "Anthropic" in result
    assert isinstance(result["OpenAI"], list)
    assert isinstance(result["Anthropic"], list)
    assert len(result["OpenAI"]) > 0
    assert len(result["Anthropic"]) > 0


@pytest.mark.asyncio
async def test_teardown(ai_assistant_service):
    """Test tearing down the AI Assistant Service."""
    # Set initialized and ready to True
    ai_assistant_service.initialized = True
    ai_assistant_service.ready = True

    # Tear down the service
    await ai_assistant_service.teardown()

    # Check that initialized and ready are False
    assert not ai_assistant_service.initialized
    assert not ai_assistant_service.ready
