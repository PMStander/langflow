"""Tests for the ComponentKnowledgeBase class."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langflow.services.ai_assistant.knowledge_base import ComponentKnowledgeBase


@pytest.fixture
def mock_settings_service():
    """Create a mock settings service."""
    settings_service = MagicMock()
    settings_service.settings.components_path = ["/path/to/components"]
    return settings_service


@pytest.fixture
def knowledge_base():
    """Create a ComponentKnowledgeBase instance."""
    return ComponentKnowledgeBase()


@pytest.mark.asyncio
async def test_build_from_registry(knowledge_base, mock_settings_service):
    """Test building the knowledge base from the registry."""
    # Mock the get_and_cache_all_types_dict function
    mock_all_types_dict = {
        "components": {
            "llms": {
                "openai": {
                    "display_name": "OpenAI",
                    "description": "OpenAI language model",
                    "template": {
                        "output_types": ["language_model"],
                        "inputs": {
                            "model_name": {"type": "str"},
                            "temperature": {"type": "float"},
                        },
                    },
                }
            },
            "prompts": {
                "prompt": {
                    "display_name": "Prompt",
                    "description": "A prompt for language models",
                    "template": {
                        "output_types": ["prompt"],
                        "inputs": {
                            "template": {"type": "str"},
                        },
                    },
                }
            },
        }
    }
    
    with patch("langflow.interface.components.get_and_cache_all_types_dict", 
              new=AsyncMock(return_value=mock_all_types_dict)):
        await knowledge_base.build_from_registry(mock_settings_service)
    
    # Check that the components were stored
    assert "llms" in knowledge_base.components
    assert "prompts" in knowledge_base.components
    assert "openai" in knowledge_base.components["llms"]
    assert "prompt" in knowledge_base.components["prompts"]
    
    # Check that the categories were extracted
    assert "llms" in knowledge_base.categories
    assert "prompts" in knowledge_base.categories
    assert "openai" in knowledge_base.categories["llms"]
    assert "prompt" in knowledge_base.categories["prompts"]


@pytest.mark.asyncio
async def test_analyze_connection_compatibility(knowledge_base):
    """Test analyzing component connection compatibility."""
    # Set up test components
    knowledge_base.components = {
        "llms": {
            "openai": {
                "display_name": "OpenAI",
                "template": {
                    "output_types": ["language_model"],
                },
            }
        },
        "chains": {
            "llm_chain": {
                "display_name": "LLM Chain",
                "template": {
                    "inputs": {
                        "llm": {"type": "language_model"},
                        "prompt": {"type": "prompt"},
                    },
                },
            }
        },
        "prompts": {
            "prompt": {
                "display_name": "Prompt",
                "template": {
                    "output_types": ["prompt"],
                },
            }
        },
    }
    
    await knowledge_base.analyze_connection_compatibility()
    
    # Check that the connection graph was built correctly
    assert "llms.openai" in knowledge_base.connection_graph
    assert "prompts.prompt" in knowledge_base.connection_graph
    
    # Check that the type compatibility was built correctly
    assert "language_model" in knowledge_base.type_compatibility
    assert "prompt" in knowledge_base.type_compatibility


@pytest.mark.asyncio
async def test_create_semantic_mappings(knowledge_base):
    """Test creating semantic mappings."""
    # Set up test components
    knowledge_base.components = {
        "llms": {
            "openai": {
                "display_name": "OpenAI",
                "description": "OpenAI language model",
                "template": {},
            }
        },
        "prompts": {
            "prompt": {
                "display_name": "Prompt Template",
                "description": "A template for prompts",
                "template": {},
            }
        },
    }
    
    await knowledge_base.create_semantic_mappings()
    
    # Check that semantic mappings were created
    assert "llms" in knowledge_base.semantic_mappings
    assert "openai" in knowledge_base.semantic_mappings
    assert "language" in knowledge_base.semantic_mappings
    assert "model" in knowledge_base.semantic_mappings
    assert "prompt" in knowledge_base.semantic_mappings
    assert "template" in knowledge_base.semantic_mappings
    
    # Check that purpose classification was created
    assert "llms" in knowledge_base.purpose_classification
    assert "prompts" in knowledge_base.purpose_classification
    assert "openai" in knowledge_base.purpose_classification["llms"]
    assert "prompt" in knowledge_base.purpose_classification["prompts"]
    assert knowledge_base.purpose_classification["llms"]["openai"] == "language_model"
    assert knowledge_base.purpose_classification["prompts"]["prompt"] == "prompt"


@pytest.mark.asyncio
async def test_get_component_info(knowledge_base):
    """Test getting component information."""
    # Set up test components
    knowledge_base.components = {
        "llms": {
            "openai": {
                "display_name": "OpenAI",
                "description": "OpenAI language model",
            }
        }
    }
    
    # Get component info
    component_info = await knowledge_base.get_component_info("llms", "openai")
    
    # Check that the correct component info was returned
    assert component_info["display_name"] == "OpenAI"
    assert component_info["description"] == "OpenAI language model"
    
    # Test with non-existent component
    component_info = await knowledge_base.get_component_info("non_existent", "component")
    assert component_info == {}
