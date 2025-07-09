from db.models import SessionLocal, AgentModel 
from db.models import AgentModel

db = SessionLocal()
agents = db.query(AgentModel).all()
print(agents)  # this should show at least one object
