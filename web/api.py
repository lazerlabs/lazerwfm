from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from lazerwfm.types import WorkflowStatus
from lazerwfm.workflow_engine import WorkflowEngine


class WorkflowInfo(BaseModel):
    """Workflow information returned by API"""

    id: str
    status: WorkflowStatus
    created_at: datetime
    result: Any | None = None
    error: str | None = None


class WorkflowList(BaseModel):
    """List of workflows with count"""

    total: int
    workflows: list[WorkflowInfo]


def create_api(engine: WorkflowEngine) -> FastAPI:
    """Create FastAPI application with workflow engine endpoints"""
    app = FastAPI(
        title="LazerWFM API",
        description="REST API for LazerWFM workflow engine",
        version="0.1.0",
    )

    @app.get("/workflows", response_model=WorkflowList, tags=["workflows"])
    async def list_workflows():
        """List all workflows in both warm and cold storage"""
        active_ids = engine._storage.get_active_workflows()
        workflows = []

        for wf_id in active_ids:
            wf = engine.get_workflow(wf_id)
            if wf:
                workflows.append(
                    WorkflowInfo(
                        id=wf.id,
                        status=wf.status,
                        created_at=wf.created_at,
                        result=wf.get_result(),
                        error=str(wf.get_error()) if wf.get_error() else None,
                    )
                )

        return WorkflowList(total=len(workflows), workflows=workflows)

    @app.get(
        "/workflows/{workflow_id}", response_model=WorkflowInfo, tags=["workflows"]
    )
    async def get_workflow(workflow_id: str):
        """Get information about a specific workflow"""
        workflow = engine.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return WorkflowInfo(
            id=workflow.id,
            status=workflow.status,
            created_at=workflow.created_at,
            result=workflow.get_result(),
            error=str(workflow.get_error()) if workflow.get_error() else None,
        )

    @app.post("/workflows/{workflow_id}/stop", tags=["workflows"])
    async def stop_workflow(workflow_id: str):
        """Stop a running workflow"""
        workflow = engine.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        await engine.stop_workflow(workflow_id)
        return {"status": "stopped"}

    @app.post("/workflows/stop-all", tags=["workflows"])
    async def stop_all_workflows():
        """Stop all running workflows"""
        await engine.stop_all_workflows()
        return {"status": "all workflows stopped"}

    @app.post("/workflows/cleanup", tags=["workflows"])
    async def cleanup_workflows(before: datetime):
        """Clean up workflows from cold storage older than the specified date"""
        await engine.cleanup_old_workflows(before)
        return {"status": "cleanup completed"}

    @app.get("/health", tags=["system"])
    async def health_check():
        """Check if the workflow engine is running"""
        active_workflows = len(engine._storage.get_active_workflows())
        return {
            "status": "healthy",
            "active_workflows": active_workflows,
            "engine_running": engine._running,
        }

    return app
