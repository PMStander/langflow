"""API endpoints for the AI Assistant Service."""

from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from langflow.services.auth.utils import get_current_active_user
from langflow.services.deps import get_settings_service
from langflow.services.ai_assistant.service import AIAssistantService

router = APIRouter(prefix="/ai-assistant", tags=["AI Assistant"])


class ClarificationQuestion(BaseModel):
    """Model for a clarification question."""

    question_id: str = Field(..., description="A unique identifier for the question")
    question: str = Field(..., description="The question to ask the user")
    options: List[str] = Field(default_factory=list, description="Possible options for the answer")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context information for the question")


class ComponentRequirement(BaseModel):
    """Model for a component requirement."""

    component_type: str = Field(..., description="The type of the component (e.g., 'llms', 'chains')")
    component_name: str = Field(..., description="The name of the component (e.g., 'openai', 'llm_chain')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters for the component")
    description: str = Field("", description="A description of what this component does in the flow")


class ConnectionRequirement(BaseModel):
    """Model for a connection requirement."""

    source_component_idx: int = Field(..., description="The index of the source component in the components list")
    target_component_idx: int = Field(..., description="The index of the target component in the components list")
    source_field: str = Field("output", description="The output field of the source component")
    target_field: str = Field(..., description="The input field of the target component")
    description: str = Field("", description="A description of what this connection represents")


class InstructionRequest(BaseModel):
    """Request model for interpreting an instruction."""

    instruction: str = Field(..., description="The natural language instruction to interpret")
    llm_provider: Optional[str] = Field(None, description="The LLM provider to use for interpretation")
    llm_model: Optional[str] = Field(None, description="The LLM model to use for interpretation")


class InstructionResponse(BaseModel):
    """Response model for an interpreted instruction."""

    instruction: str = Field(..., description="The original instruction")
    components: List[ComponentRequirement] = Field(default_factory=list, description="Required components")
    connections: List[ConnectionRequirement] = Field(default_factory=list, description="Required connections")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Global parameters")
    clarification_needed: bool = Field(False, description="Whether clarification is needed")
    clarification_questions: List[ClarificationQuestion] = Field(default_factory=list, description="Questions to ask")
    flow_description: str = Field("", description="A description of what the flow does")


class FlowRequest(BaseModel):
    """Request model for building a flow from an instruction."""

    instruction: str = Field(..., description="The natural language instruction to build a flow from")
    llm_provider: Optional[str] = Field(None, description="The LLM provider to use for interpretation")
    llm_model: Optional[str] = Field(None, description="The LLM model to use for interpretation")


class FlowResponse(BaseModel):
    """Response model for a flow built from an instruction."""

    instruction: str = Field(..., description="The original instruction")
    interpretation: Dict[str, Any] = Field(..., description="The interpreted instruction details")
    flow: Dict[str, Any] = Field(..., description="The flow data")


class ClarificationRequest(BaseModel):
    """Request model for responding to a clarification question."""

    question_id: str = Field(..., description="The ID of the question being answered")
    response: str = Field(..., description="The user's response to the question")
    instruction: str = Field(..., description="The original instruction")


class ClarificationResponse(BaseModel):
    """Response model for a clarification response."""

    question_id: str = Field(..., description="The ID of the question that was answered")
    response: str = Field(..., description="The user's response to the question")
    processed: bool = Field(..., description="Whether the response was successfully processed")
    updated_interpretation: Dict[str, Any] = Field(..., description="The updated interpretation")


class ComponentInfoRequest(BaseModel):
    """Request model for getting component information."""

    component_type: str = Field(..., description="The type of the component")
    component_name: str = Field(..., description="The name of the component")


class CompatibleComponentsRequest(BaseModel):
    """Request model for getting compatible components."""

    component_type: str = Field(..., description="The type of the component")
    component_name: str = Field(..., description="The name of the component")


class LLMProviderRequest(BaseModel):
    """Request model for setting the LLM provider."""

    provider_name: str = Field(..., description="The name of the LLM provider")
    model_name: str = Field(..., description="The name of the model to use")


def get_ai_assistant_service() -> AIAssistantService:
    """Get the AI Assistant Service instance.

    Returns:
        The AI Assistant Service instance.
    """
    from langflow.services.deps import get_service
    from langflow.services.deps import ServiceType

    # Check if service exists
    service = get_service(ServiceType.AI_ASSISTANT_SERVICE)

    # If not, create it
    if service is None:
        settings_service = get_settings_service()
        service = AIAssistantService(settings_service)

    return service


@router.post("/interpret", response_model=InstructionResponse,
            dependencies=[Depends(get_current_active_user)])
async def interpret_instruction(
    request: InstructionRequest,
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
) -> InstructionResponse:
    """Interpret a natural language instruction.

    Args:
        request: The instruction request.
        ai_assistant_service: The AI Assistant Service.

    Returns:
        The interpreted instruction details.
    """
    try:
        # Set the LLM provider and model if specified
        if request.llm_provider and request.llm_model:
            await ai_assistant_service.set_llm_provider(request.llm_provider, request.llm_model)

        # Interpret the instruction
        interpretation = await ai_assistant_service.interpret_instruction(request.instruction)
        return InstructionResponse(**interpretation)
    except ValueError as e:
        # This is likely an API key error, which we want to show to the user with a 400 status
        # so the frontend can display it properly
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interpreting instruction: {str(e)}"
        )


@router.post("/build-flow", response_model=FlowResponse,
            dependencies=[Depends(get_current_active_user)])
async def build_flow(
    request: FlowRequest,
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
) -> FlowResponse:
    """Build a flow from a natural language instruction.

    Args:
        request: The flow request.
        ai_assistant_service: The AI Assistant Service.

    Returns:
        The flow data.
    """
    try:
        # Set the LLM provider and model if specified
        if request.llm_provider and request.llm_model:
            await ai_assistant_service.set_llm_provider(request.llm_provider, request.llm_model)

        # Build the flow
        flow_data = await ai_assistant_service.build_flow_from_instruction(request.instruction)
        return FlowResponse(**flow_data)
    except ValueError as e:
        # This is likely an API key error, which we want to show to the user with a 400 status
        # so the frontend can display it properly
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error building flow: {str(e)}"
        )


@router.post("/clarify", response_model=ClarificationResponse,
            dependencies=[Depends(get_current_active_user)])
async def process_clarification(
    request: ClarificationRequest,
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
) -> ClarificationResponse:
    """Process a response to a clarification question.

    Args:
        request: The clarification request.
        ai_assistant_service: The AI Assistant Service.

    Returns:
        The updated interpretation.
    """
    try:
        # Process the clarification response
        result = await ai_assistant_service.process_clarification_response(
            request.question_id, request.response)
        return ClarificationResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing clarification: {str(e)}"
        )


@router.post("/component-info", dependencies=[Depends(get_current_active_user)])
async def get_component_info(
    request: ComponentInfoRequest,
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
) -> Dict[str, Any]:
    """Get information about a specific component.

    Args:
        request: The component info request.
        ai_assistant_service: The AI Assistant Service.

    Returns:
        Information about the component.
    """
    try:
        component_info = await ai_assistant_service.get_component_info(
            request.component_type, request.component_name)
        return component_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting component info: {str(e)}"
        )


@router.post("/compatible-components", dependencies=[Depends(get_current_active_user)])
async def get_compatible_components(
    request: CompatibleComponentsRequest,
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
) -> List[Dict[str, Any]]:
    """Get a list of components that are compatible with the specified component.

    Args:
        request: The compatible components request.
        ai_assistant_service: The AI Assistant Service.

    Returns:
        A list of compatible components.
    """
    try:
        compatible_components = await ai_assistant_service.get_compatible_components(
            request.component_type, request.component_name)
        return compatible_components
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting compatible components: {str(e)}"
        )


@router.get("/llm-providers", dependencies=[Depends(get_current_active_user)])
async def get_llm_providers(
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
) -> Dict[str, List[str]]:
    """Get a list of available LLM providers and models.

    Args:
        ai_assistant_service: The AI Assistant Service.

    Returns:
        A dictionary mapping provider names to lists of model names.
    """
    try:
        providers = await ai_assistant_service.get_available_llm_providers()
        return providers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting LLM providers: {str(e)}"
        )


@router.post("/set-llm-provider", dependencies=[Depends(get_current_active_user)])
async def set_llm_provider(
    request: LLMProviderRequest,
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
) -> Dict[str, str]:
    """Set the LLM provider and model to use for instruction parsing.

    Args:
        request: The LLM provider request.
        ai_assistant_service: The AI Assistant Service.

    Returns:
        A confirmation message.
    """
    try:
        await ai_assistant_service.set_llm_provider(request.provider_name, request.model_name)
        return {
            "message": f"LLM provider set to {request.provider_name} with model {request.model_name}",
            "provider": request.provider_name,
            "model": request.model_name
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting LLM provider: {str(e)}"
        )


class APIKeyRequest(BaseModel):
    """Request model for saving an API key."""

    key_name: str = Field(..., description="The name of the API key (e.g., 'OPENAI_API_KEY')")
    api_key: str = Field(..., description="The API key value")


@router.post("/save-api-key", dependencies=[Depends(get_current_active_user)])
async def save_api_key(
    request: APIKeyRequest,
    current_user = Depends(get_current_active_user)
) -> Dict[str, str]:
    """Save an API key for the AI Assistant.

    This endpoint saves an API key to the variable service for use by the AI Assistant.
    The key will be associated with the current user and will persist between sessions.

    Args:
        request: The API key request containing the key name and value.
        current_user: The current authenticated user.

    Returns:
        A confirmation message.
    """
    try:
        from langflow.services.deps import get_variable_service, get_db_service
        from sqlalchemy import select
        from langflow.services.database.models.variable import Variable
        from langflow.services.variable.constants import CREDENTIAL_TYPE
        from loguru import logger

        # Get the variable service
        variable_service = get_variable_service()
        db_service = get_db_service()

        logger.debug(f"Saving API key {request.key_name} for user {current_user.id}")

        # Use the session in a context manager
        async with db_service.with_session() as session:
            # Check if the variable already exists
            stmt = select(Variable).where(Variable.user_id == current_user.id, Variable.name == request.key_name)
            result = await session.execute(stmt)
            existing_variable = result.scalar_one_or_none()

            if existing_variable:
                logger.debug(f"Updating existing variable {request.key_name}")
                # Update the existing variable
                await variable_service.update_variable(
                    user_id=current_user.id,
                    name=request.key_name,
                    value=request.api_key,
                    session=session
                )
            else:
                logger.debug(f"Creating new variable {request.key_name}")
                # Create a new variable
                await variable_service.create_variable(
                    user_id=current_user.id,
                    name=request.key_name,
                    value=request.api_key,
                    default_fields=[request.key_name.lower()],
                    type_=CREDENTIAL_TYPE,
                    session=session
                )

            return {
                "message": f"API key {request.key_name} saved successfully",
                "key_name": request.key_name
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving API key: {str(e)}"
        )


@router.post("/refresh-knowledge-base", dependencies=[Depends(get_current_active_user)])
async def refresh_knowledge_base(
    ai_assistant_service: AIAssistantService = Depends(get_ai_assistant_service)
) -> Dict[str, str]:
    """Refresh the AI Assistant's knowledge base.

    This endpoint forces a refresh of the AI Assistant's knowledge base,
    ensuring that all components (including those from bundles) are available.

    Args:
        ai_assistant_service: The AI Assistant Service.

    Returns:
        A confirmation message.
    """
    try:
        await ai_assistant_service.refresh_knowledge_base()
        return {
            "message": "AI Assistant knowledge base refreshed successfully",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing knowledge base: {str(e)}"
        )


@router.get("/api-keys", dependencies=[Depends(get_current_active_user)])
async def get_api_keys(
    current_user = Depends(get_current_active_user)
) -> Dict[str, List[str]]:
    """Get the saved API keys for the AI Assistant.

    This endpoint retrieves the names of API keys saved for the current user.
    The actual key values are not returned for security reasons.

    Args:
        current_user: The current authenticated user.

    Returns:
        A dictionary with a list of API key names.
    """
    try:
        from langflow.services.deps import get_variable_service, get_db_service
        from langflow.services.variable.constants import CREDENTIAL_TYPE
        from loguru import logger

        # Get the variable service
        variable_service = get_variable_service()
        db_service = get_db_service()

        logger.debug(f"Getting API keys for user {current_user.id}")

        # Use the with_session context manager
        async with db_service.with_session() as session:
            # Get all credential variables for the user (case insensitive check)
            variables = []
            from sqlmodel import select, or_
            from langflow.services.database.models.variable import Variable

            # Query directly to get ALL variables for the user first
            stmt = select(Variable).where(Variable.user_id == current_user.id)
            all_vars = list((await session.exec(stmt)).all())

            # Filter for credential types (case insensitive) and normalized key names
            seen_names_lower = set()
            variables = []
            for var in all_vars:
                if var.type and var.type.lower() == CREDENTIAL_TYPE.lower():
                    # Use lowercase name for deduplication to handle case variations
                    if var.name.lower() not in seen_names_lower:
                        seen_names_lower.add(var.name.lower())
                        variables.append(var)

            logger.debug(f"Found {len(variables)} credential variables: {[v.name for v in variables]}")

            # Also try to get all variables for this user to see what types exist
            all_vars_stmt = select(Variable).where(Variable.user_id == current_user.id)
            all_vars = list((await session.exec(all_vars_stmt)).all())
            logger.debug(f"Total variables for user: {len(all_vars)}")
            logger.debug(f"Variable types: {set(v.type for v in all_vars if v.type)}")
            logger.debug(f"All variables: {[(v.name, v.type, v.id) for v in all_vars]}")

            # Return all credential variables as API keys without filtering
            api_key_names = [variable.name for variable in variables]
            logger.debug(f"Returning API key names: {api_key_names}")

            return {
                "api_keys": api_key_names
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting API keys: {str(e)}"
        )
