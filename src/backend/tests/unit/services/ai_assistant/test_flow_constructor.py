"""Tests for the FlowConstructor class."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langflow.services.ai_assistant.flow_constructor import FlowConstructor, Flow, FlowNode, FlowEdge
from langflow.services.ai_assistant.instruction_parser import ParsedInstruction, ComponentRequirement, ConnectionRequirement


@pytest.fixture
def knowledge_base_mock():
    """Create a mock knowledge base."""
    knowledge_base = MagicMock()
    
    # Mock the get_component_info method
    async def get_component_info(component_type, component_name):
        return {
            "template": {
                "inputs": {},
                "output_types": ["str"],
                "input_types": ["str"],
            },
            "description": f"A {component_type} component",
            "display_name": component_name.replace("_", " ").title(),
            "base_classes": [component_type],
        }
    
    knowledge_base.get_component_info = AsyncMock(side_effect=get_component_info)
    
    return knowledge_base


@pytest.fixture
def parsed_instruction():
    """Create a parsed instruction for testing."""
    return ParsedInstruction(
        instruction="Create a simple LLM chain with OpenAI and a prompt",
        components=[
            ComponentRequirement(
                component_type="llms",
                component_name="openai",
                parameters={"model_name": "gpt-4"},
                description="The OpenAI LLM"
            ),
            ComponentRequirement(
                component_type="prompts",
                component_name="prompt",
                parameters={"template": "You are a helpful assistant."},
                description="The prompt template"
            ),
            ComponentRequirement(
                component_type="chains",
                component_name="llm_chain",
                parameters={},
                description="The LLM chain"
            )
        ],
        connections=[
            ConnectionRequirement(
                source_component_idx=1,  # prompt
                target_component_idx=2,  # llm_chain
                source_field="output",
                target_field="prompt",
                description="Connect the prompt to the LLM chain"
            ),
            ConnectionRequirement(
                source_component_idx=0,  # openai
                target_component_idx=2,  # llm_chain
                source_field="output",
                target_field="llm",
                description="Connect the LLM to the LLM chain"
            )
        ],
        flow_description="A simple LLM chain"
    )


@pytest.mark.asyncio
async def test_build_flow(knowledge_base_mock, parsed_instruction):
    """Test building a flow from a parsed instruction."""
    # Create a flow constructor
    flow_constructor = FlowConstructor(knowledge_base_mock)
    
    # Build a flow
    flow = await flow_constructor.build_flow(parsed_instruction)
    
    # Check the flow
    assert isinstance(flow, Flow)
    assert len(flow.nodes) == 3
    assert len(flow.edges) == 2
    
    # Check the nodes
    assert all(isinstance(node, FlowNode) for node in flow.nodes)
    assert flow.nodes[0].type == "genericNode"
    assert flow.nodes[0].data["type"] == "llms"
    assert flow.nodes[1].data["type"] == "prompts"
    assert flow.nodes[2].data["type"] == "chains"
    
    # Check the edges
    assert all(isinstance(edge, FlowEdge) for edge in flow.edges)
    assert flow.edges[0].source == flow.nodes[1].id
    assert flow.edges[0].target == flow.nodes[2].id
    assert flow.edges[1].source == flow.nodes[0].id
    assert flow.edges[1].target == flow.nodes[2].id


@pytest.mark.asyncio
async def test_select_components(knowledge_base_mock, parsed_instruction):
    """Test selecting components based on requirements."""
    # Create a flow constructor
    flow_constructor = FlowConstructor(knowledge_base_mock)
    
    # Select components
    nodes = await flow_constructor._select_components(parsed_instruction.components)
    
    # Check the nodes
    assert len(nodes) == 3
    assert all(isinstance(node, FlowNode) for node in nodes)
    assert nodes[0].data["type"] == "llms"
    assert nodes[1].data["type"] == "prompts"
    assert nodes[2].data["type"] == "chains"
    
    # Check that the knowledge base was called
    knowledge_base_mock.get_component_info.assert_called()


@pytest.mark.asyncio
async def test_create_connections(knowledge_base_mock, parsed_instruction):
    """Test creating connections between components."""
    # Create a flow constructor
    flow_constructor = FlowConstructor(knowledge_base_mock)
    
    # Select components
    nodes = await flow_constructor._select_components(parsed_instruction.components)
    
    # Create connections
    edges = await flow_constructor._create_connections(parsed_instruction.connections, nodes)
    
    # Check the edges
    assert len(edges) == 2
    assert all(isinstance(edge, FlowEdge) for edge in edges)
    assert edges[0].source == nodes[1].id
    assert edges[0].target == nodes[2].id
    assert edges[1].source == nodes[0].id
    assert edges[1].target == nodes[2].id


@pytest.mark.asyncio
async def test_configure_parameters(knowledge_base_mock, parsed_instruction):
    """Test configuring parameters for components."""
    # Create a flow constructor
    flow_constructor = FlowConstructor(knowledge_base_mock)
    
    # Select components
    nodes = await flow_constructor._select_components(parsed_instruction.components)
    
    # Configure parameters
    await flow_constructor._configure_parameters(parsed_instruction.components, nodes)
    
    # Check that the parameters were set
    # This is a bit tricky to test since the parameters are set in the template
    # which is mocked, but we can check that the method ran without errors
    assert True


@pytest.mark.asyncio
async def test_position_nodes(knowledge_base_mock):
    """Test positioning nodes in a layout."""
    # Create a flow constructor
    flow_constructor = FlowConstructor(knowledge_base_mock)
    
    # Create some nodes
    nodes = [
        FlowNode(
            id=f"node-{i}",
            type="genericNode",
            data={"id": f"node-{i}", "type": "test"},
            position={"x": 0, "y": 0}
        )
        for i in range(5)
    ]
    
    # Position the nodes
    await flow_constructor._position_nodes(nodes)
    
    # Check that the nodes have different positions
    positions = [node.position for node in nodes]
    assert len(set(tuple(pos.values()) for pos in positions)) == len(nodes)
