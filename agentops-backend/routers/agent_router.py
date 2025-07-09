import pandas as pd
from fastapi.responses import FileResponse
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session, load_only
from sqlalchemy import asc, desc
from pydantic import BaseModel
from db.models import AgentModel, get_db
from typing import Optional, List
import logging
from utils.health_check import ping_health
from db.models import SessionLocal
from collections import Counter
from db.models import AgentModel, ArchivedAgentModel
from datetime import datetime

logger = logging.getLogger("agentops")
router = APIRouter()

class Agent(BaseModel):
    agent_id: str
    agent_name: str
    agent_type: str
    version: str
    framework: str
    owner: str
    status: str
    task: str
    health_endpoint: str
    deployed_at: str

class AgentUpgrade(BaseModel):
    version: str
    deployed_at: str

class BulkAgent(BaseModel):
    agents: List[Agent]

@router.post("/register")
def register_agent(agent: Agent, db: Session = Depends(get_db)):
    if db.query(AgentModel).filter_by(agent_id=agent.agent_id).first():
        raise HTTPException(status_code=400, detail="Agent already exists")
    db.add(AgentModel(**agent.dict()))
    db.commit()
    logger.info(f"Registered agent {agent.agent_id}")
    return {"message": "Agent registered successfully"}

@router.post("/register/bulk")
def bulk_register_agents(payload: BulkAgent, db: Session = Depends(get_db)):
    created, skipped = []
    for agent in payload.agents:
        if db.query(AgentModel).filter_by(agent_id=agent.agent_id).first():
            skipped.append(agent.agent_id)
            continue
        db.add(AgentModel(**agent.dict()))
        created.append(agent.agent_id)
    db.commit()
    logger.info(f"Bulk registration done: Created={created}, Skipped={skipped}")
    return {"registered": created, "skipped": skipped}

class UpgradeRequest(BaseModel):
    agent_id: str
    new_version: str
@router.post("/upgrade")
def upgrade_agent(request: UpgradeRequest, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter_by(agent_id=request.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    old_version = agent.version
    agent.version = request.new_version
    db.commit()
    return {
        "message": f"✅ Agent {request.agent_id} upgraded from version {old_version} to {request.new_version}"
    }


@router.get("/status/{agent_id}")
def get_agent_status(agent_id: str, db: Session = Depends(get_db)):
    try:
        agent = db.query(AgentModel).filter_by(agent_id=agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        db.refresh(agent)  # ✅ Ensure we have latest from DB
        return {
            "agent_id": agent.agent_id,
            "status": agent.status,
            "health": agent.health or "UNKNOWN"
        }
    except Exception as e:
        logger.error(f"❌ Error retrieving agent status: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/status/all")
def get_all_agents(db: Session = Depends(get_db)):
    agents = db.query(AgentModel).all()
    if not agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return [
        {
            "agent_id": a.agent_id,
            "agent_name": a.agent_name,
            "agent_type": a.agent_type,
            "version": a.version,
            "framework": a.framework,
            "owner": a.owner,
            "status": a.status,
            "task": a.task,
            "health_endpoint": a.health_endpoint,
            "deployed_at": str(a.deployed_at),
            "health": a.health
        }
        for a in agents
    ]

@router.post("/retire/{agent_id}")
def retire_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter_by(agent_id=agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # ✅ Step 1: Create archived copy
    archived = ArchivedAgentModel(
        agent_id=agent.agent_id,
        agent_name=agent.agent_name,
        agent_type=agent.agent_type,
        version=agent.version,
        framework=agent.framework,
        owner=agent.owner,
        status="retired",  # Archived agents are marked retired
        task=agent.task,
        health_endpoint=agent.health_endpoint,
        deployed_at=agent.deployed_at,
        health=agent.health
    )

    db.add(archived)  # ✅ Step 2: Insert into archived_agents
    db.delete(agent)  # ✅ Step 3: Remove from agents
    db.commit()

    logger.info(f"🗃️ Agent {agent_id} retired and archived")
    return {"message": f"🗃️ Agent {agent_id} retired and moved to archive"}

@router.get("/archived")
def list_archived_agents(db: Session = Depends(get_db)):
    archived = db.query(ArchivedAgentModel).all()
    if not archived:
        return {"message": "📦 No archived agents found"}
    
    return [
        {
            "agent_id": a.agent_id,
            "agent_name": a.agent_name,
            "agent_type": a.agent_type,
            "version": a.version,
            "framework": a.framework,
            "owner": a.owner,
            "status": a.status,
            "task": a.task,
            "health_endpoint": a.health_endpoint,
            "deployed_at": a.deployed_at,
            "health": a.health,
        }
        for a in archived
    ]
@router.post("/update-status/{agent_id}")
def update_agent_status(agent_id: str, new_status: str, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter_by(agent_id=agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.status = new_status
    db.commit()
    logger.info(f"Updated agent {agent_id} status to {new_status}")
    return {"message": f"Agent {agent_id} status updated to {new_status}"}

@router.post("/upgrade/{agent_id}")
def upgrade_agent(agent_id: str, upgrade: AgentUpgrade, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter_by(agent_id=agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.version = upgrade.version
    agent.deployed_at = upgrade.deployed_at
    db.commit()
    logger.info(f"Agent {agent_id} upgraded to version {upgrade.version}")
    return {"message": f"Agent {agent_id} upgraded to version {upgrade.version}"}

@router.get("/summary")
def agent_summary(db: Session = Depends(get_db)):
    agents = db.query(AgentModel).all()
    if not agents:
        return {"message": "No agents available"}

    summary = {
        "total_agents": len(agents),
        "by_type": dict(Counter(agent.agent_type for agent in agents)),
        "by_owner": dict(Counter(agent.owner for agent in agents)),
        "by_status": dict(Counter(agent.status for agent in agents)),
        "by_health": dict(Counter(agent.health for agent in agents)),
    }
    return summary

@router.get("/summary/owner/{owner}")
def summary_by_owner(owner: str, db: Session = Depends(get_db)):
    agents = db.query(AgentModel).filter_by(owner=owner).all()
    if not agents:
        raise HTTPException(status_code=404, detail="No agents found for owner")

    summary = {
        "total": len(agents),
        "by_status": {},
        "by_type": {},
        "by_framework": {}
    }

    for agent in agents:
        summary["by_status"][agent.status] = summary["by_status"].get(agent.status, 0) + 1
        summary["by_type"][agent.agent_type] = summary["by_type"].get(agent.agent_type, 0) + 1
        summary["by_framework"][agent.framework] = summary["by_framework"].get(agent.framework, 0) + 1

    return summary

@router.get("/list/active")
def list_active_agents(db: Session = Depends(get_db)):
    agents = db.query(AgentModel).filter_by(status="active").all()
    if not agents:
        raise HTTPException(status_code=404, detail="Not Found")
    return [
        {
            "agent_id": a.agent_id,
            "agent_name": a.agent_name,
            "agent_type": a.agent_type,
            "status": a.status
        }
        for a in agents
    ]

@router.delete("/delete/{agent_id}")
def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(AgentModel).filter_by(agent_id=agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Not Found")
    db.delete(agent)
    db.commit()
    logger.info(f"Deleted agent {agent_id}")
    return {"message": f"Agent {agent_id} deleted"}

@router.post("/monitor/health")
def monitor_agents_health(background_tasks: BackgroundTasks):
    def check_and_update():
        db = SessionLocal()
        try:
            agents = db.query(AgentModel).all()
            for agent in agents:
                try:
                    new_health = ping_health(agent.health_endpoint)
                    agent.health = new_health
                    db.commit()
                    logger.info(f"✅ Agent {agent.agent_id} health updated to {new_health}")
                except Exception as e:
                    logger.error(f"❌ Error updating health for {agent.agent_id}: {e}")
        except Exception as e:
            logger.error(f"❌ Health check process failed: {str(e)}")
        finally:
            db.close()

    background_tasks.add_task(check_and_update)
    return {"message": "✅ Health monitoring started in background"}

@router.post("/restore/{agent_id}")
def restore_archived_agent(agent_id: str, db: Session = Depends(get_db)):
    archived_agent = db.query(ArchivedAgentModel).filter_by(agent_id=agent_id).first()
    if not archived_agent:
        raise HTTPException(status_code=404, detail="Archived agent not found")

    # Prevent duplicate active agents
    existing = db.query(AgentModel).filter_by(agent_id=agent_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Agent already exists in active list")

    # ✅ Create and reinsert with updated deployed_at
    restored = AgentModel(
        agent_id=archived_agent.agent_id,
        agent_name=archived_agent.agent_name,
        agent_type=archived_agent.agent_type,
        version=archived_agent.version,
        framework=archived_agent.framework,
        owner=archived_agent.owner,
        status="active",
        task=archived_agent.task,
        health_endpoint=archived_agent.health_endpoint,
        deployed_at=datetime.now().isoformat(),  # ✅ Current timestamp
        health=archived_agent.health,
    )

    db.add(restored)
    db.delete(archived_agent)
    db.commit()

    return {"message": f"♻️ Agent {agent_id} restored and marked active with new deployed_at"}

@router.get("/list/all")
def list_all_agents(db: Session = Depends(get_db)):
    active_agents = db.query(AgentModel).all()
    archived_agents = db.query(ArchivedAgentModel).all()

    return {
        "active_agents": [
            {
                "agent_id": a.agent_id,
                "agent_name": a.agent_name,
                "status": a.status,
                "health": a.health
            } for a in active_agents
        ],
        "archived_agents": [
            {
                "agent_id": a.agent_id,
                "agent_name": a.agent_name,
                "status": a.status,
                "health": a.health
            } for a in archived_agents
        ]
    }
def get_health_status(url: str) -> str:
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return "Healthy"
        return "Unhealthy"
    except Exception:
        return "Unreachable"
@router.get("/export")
def export_agents(
    status: Optional[str] = None,
    owner: Optional[str] = None,
    framework: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    skip: int = 0,
    limit: int = 100,
    file_format: str = "csv",
    db: Session = Depends(get_db)
):
    def apply_filters(query, Model):
        if status:
            query = query.filter(Model.status == status)
        if owner:
            query = query.filter(Model.owner == owner)
        if framework:
            query = query.filter(Model.framework == framework)
        if search:
            query = query.filter(Model.agent_name.ilike(f"%{search}%"))
        return query

    def apply_sorting(query, Model):
        if sort_by:
            col = getattr(Model, sort_by, None)
            if col is not None:
                query = query.order_by(col.desc() if sort_order == "desc" else col.asc())
        return query

    def get_health_status(url: str) -> str:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return "Healthy"
            return "Unhealthy"
        except Exception:
            return "Unreachable"

    # Active Agents
    active_query = apply_filters(db.query(AgentModel), AgentModel)
    active_query = apply_sorting(active_query, AgentModel)
    active_agents = active_query.offset(skip).limit(limit).all()

    # Archived Agents
    archived_query = apply_filters(db.query(ArchivedAgentModel), ArchivedAgentModel)
    archived_query = apply_sorting(archived_query, ArchivedAgentModel)
    archived_agents = archived_query.offset(skip).limit(limit).all()

    # Combine & prepare for export
    combined = [
        {**a.__dict__, "source": "active"} for a in active_agents
    ] + [
        {**a.__dict__, "source": "archived"} for a in archived_agents
    ]

    for row in combined:
        row.pop("_sa_instance_state", None)
        health_url = row.get("health_endpoint")
        row["health"] = get_health_status(health_url) if health_url else "No Endpoint"

    df = pd.DataFrame(combined)

    with NamedTemporaryFile(delete=False, suffix=f".{file_format}") as tmp:
        if file_format == "csv":
            df.to_csv(tmp.name, index=False)
        elif file_format == "xlsx":
            df.to_excel(tmp.name, index=False)
        else:
            raise HTTPException(status_code=400, detail="Invalid file format")
        tmp_path = tmp.name

    return FileResponse(
        path=tmp_path,
        filename=f"agents_export.{file_format}",
        media_type="application/octet-stream"
    )
