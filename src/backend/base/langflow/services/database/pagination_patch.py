"""
Patch for fastapi_pagination to suppress SQLAlchemy deprecation warnings.

This module monkey patches the fastapi_pagination.ext.sqlalchemy module
to use session.exec() instead of session.execute() when using SQLModel.
"""

import functools
import logging
import inspect
import sys
from typing import Any, Callable, TypeVar

from fastapi_pagination.ext import sqlalchemy as fp_sqlalchemy
from fastapi_pagination.flow import flow

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar("T")


def patch_sqlalchemy_pagination():
    """
    Patch the fastapi_pagination.ext.sqlalchemy module to use session.exec()
    instead of session.execute() when using SQLModel.
    """
    try:
        # Get the original _limit_offset_flow function
        original_limit_offset_flow = fp_sqlalchemy._limit_offset_flow

        # Create a patched version that uses exec() instead of execute() when available
        @flow
        def patched_limit_offset_flow(query: Any, conn: Any, raw_params: Any) -> Any:
            query = fp_sqlalchemy.create_paginate_query(query, raw_params)

            # Check if conn has exec method (SQLModel)
            if hasattr(conn, "exec"):
                try:
                    items = yield conn.exec(query)
                except Exception as e:
                    # Fall back to original implementation if exec fails
                    logger.debug(f"Using exec() failed, falling back to execute(): {e}")
                    items = yield conn.execute(query)
            else:
                # Use original implementation for non-SQLModel sessions
                items = yield conn.execute(query)

            return items

        # Replace the original function with our patched version
        fp_sqlalchemy._limit_offset_flow = patched_limit_offset_flow
        logger.info("Successfully patched fastapi_pagination for SQLModel compatibility")

    except Exception as e:
        logger.warning(f"Failed to patch fastapi_pagination: {e}")


# Apply the patch when this module is imported
patch_sqlalchemy_pagination()
