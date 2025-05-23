"""Build utilities for the API."""

import uuid
from typing import Any

from langflow.graph.graph.base import Graph
from langflow.services.database.models.flow.model import Flow


async def _get_flow_name(flow_id: uuid.UUID) -> str:
    """Get the flow name from the database."""
    from langflow.services.deps import session_scope
    from sqlmodel import select

    async with session_scope() as session:
        result = await session.exec(select(Flow.name).where(Flow.id == flow_id))
        return result.first() or ""


async def build_graph_from_data(flow_id: uuid.UUID | str, payload: dict, **kwargs):
    """Build and cache the graph."""
    # Get flow name
    if "flow_name" not in kwargs:
        flow_name = await _get_flow_name(flow_id if isinstance(flow_id, uuid.UUID) else uuid.UUID(flow_id))
    else:
        flow_name = kwargs["flow_name"]
    str_flow_id = str(flow_id)
    session_id = kwargs.get("session_id") or str_flow_id

    graph = Graph.from_payload(payload, str_flow_id, flow_name, kwargs.get("user_id"))
    for vertex_id in graph.has_session_id_vertices:
        vertex = graph.get_vertex(vertex_id)
        if vertex is None:
            msg = f"Vertex {vertex_id} not found"
            raise ValueError(msg)
        if not vertex.raw_params.get("session_id"):
            vertex.update_raw_params({"session_id": session_id}, overwrite=True)

    graph.session_id = session_id
    await graph.initialize_run()
    return graph


async def build_graph_from_db_no_cache(flow_id: uuid.UUID, session: Any, **kwargs):
    """Build and cache the graph."""
    flow: Flow | None = await session.get(Flow, flow_id)
    if not flow or not flow.data:
        msg = "Invalid flow ID"
        raise ValueError(msg)
    kwargs["user_id"] = kwargs.get("user_id") or str(flow.user_id)
    return await build_graph_from_data(flow_id, flow.data, flow_name=flow.name, **kwargs)


async def build_graph_from_db(flow_id: uuid.UUID, session: Any, chat_service: Any, **kwargs):
    graph = await build_graph_from_db_no_cache(flow_id=flow_id, session=session, **kwargs)
    await chat_service.set_cache(str(flow_id), graph)
    return graph


async def build_and_cache_graph_from_data(
    flow_id: uuid.UUID | str,
    chat_service: Any,
    graph_data: dict,
):
    """Build and cache the graph."""
    # Convert flow_id to str if it's UUID
    str_flow_id = str(flow_id) if isinstance(flow_id, uuid.UUID) else flow_id
    graph = Graph.from_payload(graph_data, str_flow_id)
    await chat_service.set_cache(str_flow_id, graph)
    return graph


def get_top_level_vertices(graph_data: dict) -> list[str]:
    """Get the top level vertices from the graph data."""
    # Get all target vertices
    target_vertices = set()
    for edge in graph_data.get("edges", []):
        target_vertices.add(edge.get("target"))

    # Get all vertices that are not targets
    top_level_vertices = []
    for node in graph_data.get("nodes", []):
        if node.get("id") not in target_vertices:
            top_level_vertices.append(node.get("id"))

    return top_level_vertices
