"""AI Assistant module for Langflow.

This module provides the AI Assistant Service that helps users build flows through natural language instructions.
"""

from langflow.services.ai_assistant.service import AIAssistantService
from langflow.services.ai_assistant.knowledge_base import ComponentKnowledgeBase
from langflow.services.ai_assistant.instruction_parser import InstructionParser, ParsedInstruction
from langflow.services.ai_assistant.flow_constructor import FlowConstructor, Flow, FlowNode, FlowEdge

__all__ = ["AIAssistantService", "ComponentKnowledgeBase", "InstructionParser", "ParsedInstruction",
           "FlowConstructor", "Flow", "FlowNode", "FlowEdge"]
