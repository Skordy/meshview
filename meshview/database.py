from meshview import models
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import event

engine = None
async_session = None


def init_database(database_connection_string, read_only=False):
    global engine, async_session

    kwargs = {"echo": False}

    if database_connection_string.startswith("sqlite"):
        if read_only:
            kwargs["connect_args"] = {"uri": True}
            if "?" not in database_connection_string:
                database_connection_string += "?mode=ro"
            else:
                database_connection_string += "&mode=ro"
        else:
            kwargs["connect_args"] = {
                "timeout": 60,
                "check_same_thread": False
            }
    else:
        kwargs["pool_size"] = 20
        kwargs["max_overflow"] = 50

    engine = create_async_engine(database_connection_string, **kwargs)
    
    # Set WAL mode via pragma for SQLite (only if not read-only)
    if database_connection_string.startswith("sqlite") and not read_only:
        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA temp_store=memory")
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
            cursor.close()
    
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
