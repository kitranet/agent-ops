from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ✅ Database setup
DATABASE_URL = "sqlite:///./agentops.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ✅ SQLAlchemy model definition (matches with your FastAPI models)
class AgentModel(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, index=True)
    agent_name = Column(String)
    agent_type = Column(String)
    version = Column(String)
    framework = Column(String)
    owner = Column(String)
    status = Column(String)
    task = Column(String)
    health_endpoint = Column(String)
    deployed_at = Column(String)  # If needed, change to DateTime
    health = Column(String, default="UNKNOWN")  # ✅ New field for health monitoring

# ✅ Archival table definition (right after AgentModel)
class ArchivedAgentModel(Base):
    __tablename__ = "archived_agents"

    agent_id = Column(String, primary_key=True, index=True)
    agent_name = Column(String)
    agent_type = Column(String)
    version = Column(String)
    framework = Column(String)
    owner = Column(String)
    status = Column(String)
    task = Column(String)
    health_endpoint = Column(String)
    deployed_at = Column(String)
    health = Column(String)

# ✅ Create tables (auto-run on startup, only once for SQLite)
Base.metadata.create_all(bind=engine)

# ✅ Dependency to get DB session for routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
