"""
Database migration utilities with improved error handling and retry logic.
"""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine


class MigrationError(Exception):
    """Custom exception for migration errors."""
    pass


class DatabaseMigrationManager:
    """Manages database migrations with retry logic and lock handling."""

    def __init__(self, engine: AsyncEngine, alembic_cfg_path: str, max_retries: int = 5, retry_delay: int = 2):
        self.engine = engine
        self.alembic_cfg_path = alembic_cfg_path
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.lock_timeout = 30  # seconds

    async def wait_for_lock_release(self) -> bool:
        """Wait for any existing migration locks to be released."""
        logger.info("Checking for existing migration locks...")

        for attempt in range(self.max_retries):
            try:
                async with self.engine.begin() as conn:
                    # Check if advisory lock is available
                    result = await conn.execute(
                        text("SELECT pg_try_advisory_lock(112233) as lock_acquired")
                    )
                    lock_acquired = result.scalar()

                    if lock_acquired:
                        # Release the lock immediately since we're just testing
                        await conn.execute(text("SELECT pg_advisory_unlock(112233)"))
                        logger.info("No migration locks detected")
                        return True
                    else:
                        logger.warning(f"Migration lock detected, waiting... (attempt {attempt + 1}/{self.max_retries})")
                        await asyncio.sleep(self.retry_delay)

            except Exception as e:
                logger.warning(f"Error checking migration lock: {e}")
                await asyncio.sleep(self.retry_delay)

        logger.error("Migration lock timeout - proceeding anyway")
        return False

    async def force_release_locks(self) -> None:
        """Force release any stuck migration locks."""
        logger.warning("Attempting to force release migration locks...")

        try:
            async with self.engine.begin() as conn:
                # Force release advisory locks
                await conn.execute(text("SELECT pg_advisory_unlock_all()"))
                logger.info("Successfully released all advisory locks")

        except Exception as e:
            logger.error(f"Failed to force release locks: {e}")

    async def get_current_revision(self) -> str | None:
        """Get the current database revision."""
        try:
            async with self.engine.begin() as conn:
                # Check if alembic_version table exists
                result = await conn.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_name = 'alembic_version'
                        )
                    """)
                )

                if not result.scalar():
                    logger.info("No alembic_version table found - database not initialized")
                    return None

                # Get current revision
                result = await conn.execute(text("SELECT version_num FROM alembic_version"))
                revision = result.scalar()
                logger.info(f"Current database revision: {revision}")
                return revision

        except Exception as e:
            logger.error(f"Error getting current revision: {e}")
            return None

    async def check_migration_needed(self) -> bool:
        """Check if migrations are needed."""
        try:
            # Load Alembic configuration
            alembic_cfg = Config(self.alembic_cfg_path)

            # Set the script location - derive from alembic.ini path
            from pathlib import Path
            alembic_ini_path = Path(self.alembic_cfg_path)
            script_location = alembic_ini_path.parent / "alembic"
            alembic_cfg.set_main_option("script_location", str(script_location))

            # Verify script location exists
            if not script_location.exists():
                logger.warning(f"Alembic script location does not exist: {script_location}")
                return True  # Assume migration needed if script location doesn't exist

            script_dir = ScriptDirectory.from_config(alembic_cfg)

            # Get head revision from scripts
            head_revision = script_dir.get_current_head()
            logger.info(f"Head revision from scripts: {head_revision}")

            # Get current database revision
            current_revision = await self.get_current_revision()

            if current_revision is None:
                logger.info("Database not initialized - migrations needed")
                return True

            if current_revision != head_revision:
                logger.info(f"Migration needed: {current_revision} -> {head_revision}")
                return True

            logger.info("Database is up to date")
            return False

        except Exception as e:
            logger.error(f"Error checking migration status: {e}")
            return True  # Assume migration needed if we can't check

    async def run_migrations_with_retry(self) -> bool:
        """Run database migrations with retry logic."""
        logger.info("Starting database migration process...")

        # Wait for any existing locks to be released
        await self.wait_for_lock_release()

        # Check if migrations are actually needed
        if not await self.check_migration_needed():
            logger.info("No migrations needed")
            return True

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Migration attempt {attempt + 1}/{self.max_retries}")

                # Run migrations
                await self._run_migrations()

                logger.info("Database migrations completed successfully")
                return True

            except OperationalError as e:
                if "lock timeout" in str(e).lower() or "could not obtain lock" in str(e).lower():
                    logger.warning(f"Migration lock timeout on attempt {attempt + 1}: {e}")

                    if attempt < self.max_retries - 1:
                        # Force release locks and retry
                        await self.force_release_locks()
                        await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        logger.error("Max retries reached for migration lock timeout")
                        raise MigrationError(f"Migration failed after {self.max_retries} attempts due to lock timeout")
                else:
                    logger.error(f"Database operational error: {e}")
                    raise MigrationError(f"Migration failed due to database error: {e}")

            except Exception as e:
                logger.error(f"Unexpected migration error on attempt {attempt + 1}: {e}")

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    raise MigrationError(f"Migration failed after {self.max_retries} attempts: {e}")

        return False

    async def _run_migrations(self) -> None:
        """Run the actual migrations."""
        # Load Alembic configuration
        alembic_cfg = Config(self.alembic_cfg_path)

        # Set the database URL in the config
        alembic_cfg.set_main_option("sqlalchemy.url", str(self.engine.url))

        # Set the script location - derive from alembic.ini path
        from pathlib import Path
        alembic_ini_path = Path(self.alembic_cfg_path)
        script_location = alembic_ini_path.parent / "alembic"
        alembic_cfg.set_main_option("script_location", str(script_location))

        logger.info(f"Using script location: {script_location}")
        logger.info(f"Alembic config path: {self.alembic_cfg_path}")

        # Verify script location exists
        if not script_location.exists():
            raise MigrationError(f"Alembic script location does not exist: {script_location}")

        # Run migrations to head
        logger.info("Running Alembic upgrade to head...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic upgrade completed")


@asynccontextmanager
async def migration_context(engine: AsyncEngine, alembic_cfg_path: str) -> AsyncGenerator[DatabaseMigrationManager, None]:
    """Context manager for database migrations."""
    manager = DatabaseMigrationManager(engine, alembic_cfg_path)
    try:
        yield manager
    finally:
        # Cleanup: ensure locks are released
        try:
            await manager.force_release_locks()
        except Exception as e:
            logger.warning(f"Error during migration cleanup: {e}")


async def run_database_migrations(engine: AsyncEngine, alembic_cfg_path: str) -> bool:
    """
    Run database migrations with improved error handling.

    Args:
        engine: SQLAlchemy async engine
        alembic_cfg_path: Path to alembic.ini configuration file

    Returns:
        bool: True if migrations completed successfully, False otherwise
    """
    try:
        async with migration_context(engine, alembic_cfg_path) as manager:
            return await manager.run_migrations_with_retry()
    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        return False
