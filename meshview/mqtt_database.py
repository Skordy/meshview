from meshview import models
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import event

def init_database(database_connection_string):
    global engine, async_session
    kwargs = {}
    if database_connection_string.startswith('sqlite'):
        kwargs["connect_args"] = {
            "timeout": 60,
            "check_same_thread": False
        }
    else:
        kwargs['pool_size'] = 20
        kwargs['max_overflow'] = 50
    
    engine = create_async_engine(database_connection_string, echo=False, **kwargs)
    
    # Set WAL mode via pragma for SQLite
    if database_connection_string.startswith('sqlite'):
        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA temp_store=memory")
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
            cursor.close()
    
    async_session = async_sessionmaker(engine, expire_on_commit=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
