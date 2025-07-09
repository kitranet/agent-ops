from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.agent_router import router as agent_router
import logging
import os

# ✅ Setup logging
log_dir = "logs"
log_file = os.path.join(log_dir, "agent_activity.log")
os.makedirs(log_dir, exist_ok=True)

# Root logger setup
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# Separate logger for health checks
health_logger = logging.getLogger("agentops.health")
health_logger.setLevel(logging.INFO)

# ✅ FastAPI app
app = FastAPI(title="AgentOps API")

# Enable CORS for all origins and methods (optional: restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include routers
app.include_router(agent_router, prefix="/agents")

# ✅ Root endpoint
@app.get("/")
def root():
    logging.info("✅ AgentOps API root accessed.")
    return {"message": "AgentOps API is live"}

# ✅ Log startup
@app.on_event("startup")
def startup_event():
    logging.info("🚀 AgentOps API started and ready to serve requests.")
