"""Utility functions for the API."""

import re
import uuid
from datetime import timedelta
from enum import Enum
from typing import Any, Dict, List

from fastapi import Cookie, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from langflow.services.database.models.flow.model import Flow
from langflow.services.database.models.user.model import User
from langflow.services.deps import session_scope

API_WORDS = ["api", "key", "token"]

class EventDeliveryType(str, Enum):
    STREAMING = "streaming"
    DIRECT = "direct"
    POLLING = "polling"


def has_api_terms(word: str):
    return "api" in word and ("key" in word or ("token" in word and "tokens" not in word))


def remove_api_keys(flow_data: Dict) -> Dict:
    """Remove API keys from flow data."""
    if not flow_data:
        return flow_data

    # If flow_data has a 'data' key, process it
    if "data" in flow_data and flow_data["data"]:
        nodes_with_api = []
        # Nodes are in flow_data['data']['nodes']
        if "nodes" in flow_data["data"]:
            for node in flow_data["data"]["nodes"]:
                template_keys = []
                # Check if the node has a template
                if "template" in node and node["template"]:
                    # Iterate over the template keys
                    for key, value in node["template"].items():
                        # Skip if the value is not a dict
                        if not isinstance(value, dict):
                            continue
                        # Check if the key has 'api', 'key', 'token' in it
                        # or if the key is 'openai_api_key' or 'anthropic_api_key'
                        # or if the value has a field 'password' set to True
                        if (
                            has_api_terms(key.lower())
                            or key.lower() in ["openai_api_key", "anthropic_api_key"]
                            or (
                                "password" in value
                                and value["password"]
                                and value.get("value")
                            )
                        ):
                            template_keys.append(key)
                            if node["id"] not in nodes_with_api:
                                nodes_with_api.append(node["id"])

                    # Remove the API keys
                    for key in template_keys:
                        if "value" in node["template"][key]:
                            node["template"][key]["value"] = ""

    return flow_data


def validate_is_component(flows: List[Flow]) -> List[Flow]:
    """Validate if a flow is a component."""
    for flow in flows:
        if not flow.data:
            flow.is_component = False
            continue

        if "nodes" not in flow.data:
            flow.is_component = False
            continue

        # Check if there's at least one node with a display_name
        # that contains 'Input' and one node with a display_name
        # that contains 'Output'
        input_node = False
        output_node = False
        for node in flow.data["nodes"]:
            if "display_name" in node:
                if "Input" in node["display_name"]:
                    input_node = True
                if "Output" in node["display_name"]:
                    output_node = True

        flow.is_component = input_node and output_node

    return flows


async def cascade_delete_flow(session: AsyncSession, flow_id: uuid.UUID) -> None:
    """Delete a flow and all its related objects."""
    # Get the flow
    flow = (await session.exec(Flow.select.where(Flow.id == flow_id))).first()
    if flow:
        # Delete the flow
        await session.delete(flow)


def format_elapsed_time(elapsed_time: float) -> str:
    """Format elapsed time to a human-readable format coming from perf_counter().

    - Less than 1 second: returns milliseconds
    - Less than 1 minute: returns seconds rounded to 2 decimals
    - 1 minute or more: returns minutes and seconds
    """
    delta = timedelta(seconds=elapsed_time)
    if delta < timedelta(seconds=1):
        milliseconds = round(delta / timedelta(milliseconds=1))
        return f"{milliseconds} ms"

    if delta < timedelta(minutes=1):
        seconds = round(elapsed_time, 2)
        unit = "second" if seconds == 1 else "seconds"
        return f"{seconds} {unit}"

    minutes, seconds = divmod(round(elapsed_time), 60)
    if minutes == 1:
        return f"{minutes} minute, {seconds} seconds"
    return f"{minutes} minutes, {seconds} seconds"


def format_exception_message(exc: Exception) -> str:
    """Format an exception message for returning to the frontend."""
    return str(exc)


def parse_exception(exc: Exception) -> tuple[str, str]:
    """Parse an exception and return the error type and message."""
    error_type = exc.__class__.__name__
    error_message = format_exception_message(exc)
    return error_type, error_message


def parse_value(value: Any, input_type: str) -> Any:
    """Helper function to parse the value based on input type."""
    from ast import literal_eval

    if value == "":
        return {} if input_type == "DictInput" else value
    if input_type == "IntInput":
        return int(value) if value is not None else None
    if input_type == "FloatInput":
        return float(value) if value is not None else None
    if input_type == "DictInput":
        if isinstance(value, dict):
            return value
        try:
            return literal_eval(value) if value is not None else {}
        except (ValueError, SyntaxError):
            return {}
    return value


def get_suggestion_message(outdated_components: list[str]) -> str:
    """Get the suggestion message for the outdated components."""
    count = len(outdated_components)
    if count == 0:
        return "The flow contains no outdated components."
    if count == 1:
        return (
            "The flow contains 1 outdated component. "
            f"We recommend updating the following component: {outdated_components[0]}."
        )
    components = ", ".join(outdated_components)
    return (
        f"The flow contains {count} outdated components. We recommend updating the following components: {components}."
    )


async def check_langflow_version(component) -> None:
    """Check if the component is compatible with the current version of Langflow."""
    from loguru import logger
    from langflow.utils.version import get_version_info
    from langflow.services.store.utils import get_lf_version_from_pypi

    __version__ = get_version_info()["version"]

    if not component.last_tested_version:
        component.last_tested_version = __version__

    langflow_version = await get_lf_version_from_pypi()
    if langflow_version is None:
        raise HTTPException(status_code=500, detail="Unable to verify the latest version of Langflow")
    if langflow_version != component.last_tested_version:
        logger.warning(
            f"Your version of Langflow ({component.last_tested_version}) is outdated. "
            f"Please update to the latest version ({langflow_version}) and try again."
        )


async def verify_public_flow_and_get_user(flow_id: uuid.UUID, client_id: str | None) -> tuple[User, uuid.UUID]:
    """Verify a public flow request and generate a deterministic flow ID.

    This utility function:
    1. Checks that a client_id cookie is provided
    2. Verifies the flow exists and is marked as PUBLIC
    3. Creates a deterministic UUID based on client_id and original flow_id
    4. Retrieves the flow owner user for permission purposes

    This function is used to support public flow endpoints that don't require
    authentication but still need to operate within the permission model.

    Args:
        flow_id: The original flow ID to verify
        client_id: The client ID from the request cookie

    Returns:
        tuple: (flow owner user, deterministic flow ID for tracking)

    Raises:
        HTTPException:
            - 400 if no client_id is provided
            - 403 if flow doesn't exist or isn't public
            - 403 if unable to retrieve the flow owner user
            - 403 if user is not found for public flow
    """
    if not client_id:
        raise HTTPException(status_code=400, detail="No client_id cookie found")

    # Check if the flow is public
    async with session_scope() as session:
        from sqlmodel import select

        from langflow.services.database.models.flow.model import AccessTypeEnum, Flow

        flow = (await session.exec(select(Flow).where(Flow.id == flow_id))).first()
        if not flow or flow.access_type is not AccessTypeEnum.PUBLIC:
            raise HTTPException(status_code=403, detail="Flow is not public")

        # Get the user who owns the flow
        if not flow.user_id:
            raise HTTPException(status_code=403, detail="Flow has no owner")

        from langflow.services.database.models.user.model import User

        user = (await session.exec(select(User).where(User.id == flow.user_id))).first()
        if not user:
            raise HTTPException(status_code=403, detail="User not found for public flow")

        # Create a deterministic UUID based on client_id and flow_id
        # This ensures the same client always gets the same session ID for the same flow
        combined = f"{client_id}:{flow_id}"
        deterministic_id = uuid.uuid5(uuid.NAMESPACE_URL, combined)

        return user, deterministic_id
