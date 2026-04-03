from sqlmodel import Session, create_engine
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

def get_db():
    with Session(engine) as session:
        yield session

# Alias for compatibility
get_session = get_db
