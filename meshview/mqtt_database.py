from meshview import models
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

def init_database(database_connection_string):
    global engine, async_session
    kwargs = {}
    if database_connection_string.startswith('sqlite'):
        # Enable WAL mode and increase timeout for concurrent access
        kwargs["connect_args"] = {
            "timeout": 60,
            "check_same_thread": False
        }
        # Add WAL mode to connection string
        if "?" not in database_connection_string:
            database_connection_string += "?journal_mode=WAL&synchronous=NORMAL"
        else:
            database_connection_string += "&journal_mode=WAL&synchronous=NORMAL"
    else:
        kwargs['pool_size'] = 20
        kwargs['max_overflow'] = 50
    
    engine = create_async_engine(database_connection_string, echo=False, **kwargs)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
