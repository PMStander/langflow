"""Tests for the InstructionParser class."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langflow.services.ai_assistant.instruction_parser import InstructionParser, ParsedInstruction


@pytest.fixture
def mock_knowledge_base():
    """Create a mock knowledge base."""
    knowledge_base = MagicMock()
    
    # Mock components
    knowledge_base.components = {
        "llms": {
            "openai": {
                "display_name": "OpenAI",
                "description": "OpenAI language model",
            },
            "anthropic": {
                "display_name": "Anthropic",
                "description": "Anthropic language model",
            },
        },
        "chains": {
            "llm_chain": {
                "display_name": "LLM Chain",
                "description": "A chain that uses an LLM",
            },
        },
        "prompts": {
            "prompt": {
                "display_name": "Prompt",
                "description": "A prompt for language models",
            },
        },
    }
    
    # Mock categories
    knowledge_base.categories = {
        "llms": ["openai", "anthropic"],
        "chains": ["llm_chain"],
        "prompts": ["prompt"],
    }
    
    # Mock connection graph
    knowledge_base.connection_graph = {
        "llms.openai": {
            "chains.llm_chain": {
                "output": "llm"
            }
        },
        "prompts.prompt": {
            "chains.llm_chain": {
                "output": "prompt"
            }
        },
    }
    
    return knowledge_base


@pytest.fixture
def mock_settings_service():
    """Create a mock settings service."""
    settings_service = MagicMock()
    return settings_service


@pytest.fixture
def instruction_parser(mock_knowledge_base, mock_settings_service):
    """Create an InstructionParser instance with mocked dependencies."""
    parser = InstructionParser(mock_knowledge_base, mock_settings_service)
    return parser


@pytest.mark.asyncio
async def test_set_llm_provider(instruction_parser):
    """Test setting the LLM provider and model."""
    # Set the LLM provider and model
    await instruction_parser.set_llm_provider("OpenAI", "gpt-4")
    
    # Check that the provider and model were set
    assert instruction_parser.llm_provider == "OpenAI"
    assert instruction_parser.llm_model == "gpt-4"


@pytest.mark.asyncio
async def test_parse_instruction_success(instruction_parser):
    """Test parsing an instruction successfully."""
    # Mock the _get_llm_response method
    llm_response = json.dumps({
        "components": [
            {
                "component_type": "llms",
                "component_name": "openai",
                "parameters": {"model": "gpt-4"},
                "description": "The language model"
            },
            {
                "component_type": "prompts",
                "component_name": "prompt",
                "parameters": {"template": "Hello, world!"},
                "description": "The prompt template"
            },
            {
                "component_type": "chains",
                "component_name": "llm_chain",
                "parameters": {},
                "description": "The LLM chain"
            }
        ],
        "connections": [
            {
                "source_component_idx": 0,
                "target_component_idx": 2,
                "source_field": "output",
                "target_field": "llm",
                "description": "Connect the LLM to the chain"
            },
            {
                "source_component_idx": 1,
                "target_component_idx": 2,
                "source_field": "output",
                "target_field": "prompt",
                "description": "Connect the prompt to the chain"
            }
        ],
        "parameters": {},
        "clarification_needed": False,
        "clarification_questions": [],
        "flow_description": "A simple LLM chain"
    })
    
    instruction_parser._get_llm_response = AsyncMock(return_value=llm_response)
    
    # Parse an instruction
    result = await instruction_parser.parse_instruction("Create a simple LLM chain")
    
    # Check that the instruction parser called _get_llm_response
    instruction_parser._get_llm_response.assert_called_once_with("Create a simple LLM chain")
    
    # Check the result
    assert isinstance(result, ParsedInstruction)
    assert result.instruction == "Create a simple LLM chain"
    assert len(result.components) == 3
    assert len(result.connections) == 2
    assert result.flow_description == "A simple LLM chain"
    assert not result.clarification_needed
    assert not result.clarification_questions


@pytest.mark.asyncio
async def test_parse_instruction_with_clarification(instruction_parser):
    """Test parsing an instruction that requires clarification."""
    # Mock the _get_llm_response method
    llm_response = json.dumps({
        "components": [
            {
                "component_type": "llms",
                "component_name": "openai",
                "parameters": {"model": "gpt-4"},
                "description": "The language model"
            }
        ],
        "connections": [],
        "parameters": {},
        "clarification_needed": True,
        "clarification_questions": [
            {
                "question_id": "model_type",
                "question": "Which model would you like to use?",
                "options": ["gpt-3.5-turbo", "gpt-4"]
            }
        ],
        "flow_description": "An LLM-based application"
    })
    
    instruction_parser._get_llm_response = AsyncMock(return_value=llm_response)
    
    # Parse an instruction
    result = await instruction_parser.parse_instruction("Create an AI assistant")
    
    # Check that the instruction parser called _get_llm_response
    instruction_parser._get_llm_response.assert_called_once_with("Create an AI assistant")
    
    # Check the result
    assert isinstance(result, ParsedInstruction)
    assert result.instruction == "Create an AI assistant"
    assert len(result.components) == 1
    assert not result.connections
    assert result.flow_description == "An LLM-based application"
    assert result.clarification_needed
    assert len(result.clarification_questions) == 1
    assert result.clarification_questions[0].question_id == "model_type"
    assert result.clarification_questions[0].question == "Which model would you like to use?"
    assert result.clarification_questions[0].options == ["gpt-3.5-turbo", "gpt-4"]


@pytest.mark.asyncio
async def test_parse_instruction_with_invalid_component(instruction_parser):
    """Test parsing an instruction with an invalid component."""
    # Mock the _get_llm_response method
    llm_response = json.dumps({
        "components": [
            {
                "component_type": "invalid_type",
                "component_name": "invalid_name",
                "parameters": {},
                "description": "An invalid component"
            }
        ],
        "connections": [],
        "parameters": {},
        "clarification_needed": False,
        "clarification_questions": [],
        "flow_description": "An invalid flow"
    })
    
    instruction_parser._get_llm_response = AsyncMock(return_value=llm_response)
    
    # Parse an instruction
    result = await instruction_parser.parse_instruction("Create an invalid flow")
    
    # Check that the instruction parser called _get_llm_response
    instruction_parser._get_llm_response.assert_called_once_with("Create an invalid flow")
    
    # Check the result
    assert isinstance(result, ParsedInstruction)
    assert result.instruction == "Create an invalid flow"
    assert len(result.components) == 1
    assert not result.connections
    assert result.flow_description == "An invalid flow"
    assert result.clarification_needed
    assert len(result.clarification_questions) == 1
    assert "invalid_component_type_0" in result.clarification_questions[0].question_id
    assert "invalid_type" in result.clarification_questions[0].question


@pytest.mark.asyncio
async def test_parse_instruction_with_invalid_connection(instruction_parser):
    """Test parsing an instruction with an invalid connection."""
    # Mock the _get_llm_response method
    llm_response = json.dumps({
        "components": [
            {
                "component_type": "llms",
                "component_name": "openai",
                "parameters": {},
                "description": "The language model"
            },
            {
                "component_type": "prompts",
                "component_name": "prompt",
                "parameters": {},
                "description": "The prompt template"
            }
        ],
        "connections": [
            {
                "source_component_idx": 0,
                "target_component_idx": 1,
                "source_field": "output",
                "target_field": "input",
                "description": "An invalid connection"
            }
        ],
        "parameters": {},
        "clarification_needed": False,
        "clarification_questions": [],
        "flow_description": "A flow with an invalid connection"
    })
    
    instruction_parser._get_llm_response = AsyncMock(return_value=llm_response)
    
    # Parse an instruction
    result = await instruction_parser.parse_instruction("Create a flow with an invalid connection")
    
    # Check that the instruction parser called _get_llm_response
    instruction_parser._get_llm_response.assert_called_once_with("Create a flow with an invalid connection")
    
    # Check the result
    assert isinstance(result, ParsedInstruction)
    assert result.instruction == "Create a flow with an invalid connection"
    assert len(result.components) == 2
    assert len(result.connections) == 1
    assert result.flow_description == "A flow with an invalid connection"
    assert result.clarification_needed
    assert len(result.clarification_questions) == 1
    assert "invalid_connection_0" in result.clarification_questions[0].question_id
    assert "not valid" in result.clarification_questions[0].question


@pytest.mark.asyncio
async def test_parse_llm_response_with_code_blocks(instruction_parser):
    """Test parsing an LLM response with code blocks."""
    # Mock the _get_llm_response method to return a response with code blocks
    llm_response = """```json
{
    "components": [
        {
            "component_type": "llms",
            "component_name": "openai",
            "parameters": {"model": "gpt-4"},
            "description": "The language model"
        }
    ],
    "connections": [],
    "parameters": {},
    "clarification_needed": false,
    "clarification_questions": [],
    "flow_description": "A simple LLM"
}
```"""
    
    # Parse the LLM response
    result = await instruction_parser._parse_llm_response("Create a simple LLM", llm_response)
    
    # Check the result
    assert isinstance(result, ParsedInstruction)
    assert result.instruction == "Create a simple LLM"
    assert len(result.components) == 1
    assert not result.connections
    assert result.flow_description == "A simple LLM"
    assert not result.clarification_needed
    assert not result.clarification_questions


@pytest.mark.asyncio
async def test_get_llm_response_openai(instruction_parser):
    """Test getting a response from the OpenAI API."""
    # Mock the ChatOpenAI class
    mock_chat = MagicMock()
    mock_chat.invoke.return_value = MagicMock(content="Test response")
    
    with patch("langchain_openai.ChatOpenAI", return_value=mock_chat):
        # Get a response from the OpenAI API
        response = await instruction_parser._call_openai("Test prompt", "gpt-4")
        
        # Check that the response is correct
        assert response == "Test response"
        
        # Check that the ChatOpenAI class was called with the correct arguments
        from langchain_openai import ChatOpenAI
        ChatOpenAI.assert_called_once()
        
        # Check that the invoke method was called
        mock_chat.invoke.assert_called_once()


@pytest.mark.asyncio
async def test_get_llm_response_anthropic(instruction_parser):
    """Test getting a response from the Anthropic API."""
    # Mock the ChatAnthropic class
    mock_chat = MagicMock()
    mock_chat.invoke.return_value = MagicMock(content="Test response")
    
    with patch("langchain_anthropic.ChatAnthropic", return_value=mock_chat):
        # Get a response from the Anthropic API
        response = await instruction_parser._call_anthropic("Test prompt", "claude-2")
        
        # Check that the response is correct
        assert response == "Test response"
        
        # Check that the ChatAnthropic class was called with the correct arguments
        from langchain_anthropic import ChatAnthropic
        ChatAnthropic.assert_called_once()
        
        # Check that the invoke method was called
        mock_chat.invoke.assert_called_once()
