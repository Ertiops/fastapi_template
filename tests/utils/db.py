from typing import Final

from alembic.autogenerate import compare_metadata
from alembic.config import Config as AlembicConfig
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, MetaData, TextClause, pool, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_engine_from_config,
)

TRUNCATE_TABLE_SQL: Final[TextClause] = text("""
DO $$
BEGIN
    PERFORM pg_advisory_lock(424242);
    EXECUTE (
        SELECT 'TRUNCATE TABLE ' || string_agg(
            format('%I.%I', schemaname, tablename), ', '
        ) || ' RESTART IDENTITY CASCADE'
        FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename <> 'alembic_version'
    );
    PERFORM pg_advisory_unlock(424242);
EXCEPTION
    WHEN UNDEFINED_TABLE THEN
        NULL;
END $$;
""")


async def truncate_tables(session: AsyncSession) -> None:
    await session.execute(TRUNCATE_TABLE_SQL)


async def run_async_migrations(
    config: AlembicConfig,
    target_metadata: MetaData,
    revision: str,
    engine: AsyncEngine | None = None,
) -> None:
    script = ScriptDirectory.from_config(config)

    def upgrade(rev, context):
        return script._upgrade_revs(revision, rev)

    if engine is None:
        engine = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            poolclass=pool.NullPool,
        )

    with EnvironmentContext(
        config,
        script=script,
        fn=upgrade,
        as_sql=False,
        starting_rev=None,
        destination_rev=revision,
    ) as context:
        async with engine.connect() as connection:
            await connection.run_sync(
                _do_run_migrations,
                target_metadata=target_metadata,
                context=context,
            )


def _do_run_migrations(
    connection: Connection,
    target_metadata: MetaData,
    context: EnvironmentContext,
) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def get_diff_db_metadata(connection: Connection, metadata: MetaData):
    migration_ctx = MigrationContext.configure(connection)
    return compare_metadata(context=migration_ctx, metadata=metadata)
