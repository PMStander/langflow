"""
Test script to verify API key functionality in the AI Assistant.
"""

import asyncio
import os
from langflow.services.deps import get_variable_service, get_session, get_db_service
from langflow.services.auth.utils import get_current_user
from langflow.services.database.models.variable import Variable
from sqlmodel import select
from loguru import logger

async def test_api_keys():
    """Test API key functionality."""
    try:
        # Get the current user and session
        session = get_session()
        user = await get_current_user(session=session)
        
        if not user:
            logger.error("No user found. Please make sure you're logged in.")
            return
        
        # Get the variable service and database service
        variable_service = get_variable_service()
        db_service = get_db_service()
        
        # Get all variables for the user
        async with db_service.with_session() as session:
            stmt = select(Variable).where(Variable.user_id == user.id)
            all_vars = list((await session.exec(stmt)).all())
            
            logger.info(f"Total variables for user: {len(all_vars)}")
            logger.info(f"Variable types: {set(v.type for v in all_vars if v.type)}")
            logger.info(f"All variables: {[(v.name, v.type, v.id, v.value if v.name.endswith('_KEY') else '***') for v in all_vars]}")
            
            # Check if OPENAI_API_KEY exists
            openai_key = None
            for var in all_vars:
                if var.name == "OPENAI_API_KEY":
                    openai_key = var.value
                    break
            
            if openai_key:
                logger.info(f"Found OPENAI_API_KEY: {openai_key[:5]}...{openai_key[-5:]}")
            else:
                logger.warning("OPENAI_API_KEY not found in the database.")
                
            # Create or update OPENAI_API_KEY
            logger.info("Creating/updating OPENAI_API_KEY...")
            
            # Check if the key exists
            stmt = select(Variable).where(Variable.user_id == user.id, Variable.name == "OPENAI_API_KEY")
            result = await session.exec(stmt)
            existing_variable = result.first()
            
            if existing_variable:
                logger.info("Updating existing OPENAI_API_KEY")
                # Update the existing variable with a test value
                await variable_service.update_variable(
                    user_id=user.id,
                    name="OPENAI_API_KEY",
                    value="sk-test-key-for-debugging-purposes-only",
                    session=session
                )
            else:
                logger.info("Creating new OPENAI_API_KEY")
                # Create a new variable with a test value
                await variable_service.create_variable(
                    user_id=user.id,
                    name="OPENAI_API_KEY",
                    value="sk-test-key-for-debugging-purposes-only",
                    default_fields=["openai_api_key"],
                    type_="credential",
                    session=session
                )
            
            # Verify the key was saved
            stmt = select(Variable).where(Variable.user_id == user.id, Variable.name == "OPENAI_API_KEY")
            result = await session.exec(stmt)
            updated_variable = result.first()
            
            if updated_variable:
                logger.info(f"OPENAI_API_KEY saved successfully: {updated_variable.value[:5]}...{updated_variable.value[-5:]}")
            else:
                logger.error("Failed to save OPENAI_API_KEY")
    
    except Exception as e:
        logger.error(f"Error testing API keys: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_api_keys())
