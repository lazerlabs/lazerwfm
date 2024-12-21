from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from lazerwfm.types import WorkflowStatus
from lazerwfm.workflow_engine import WorkflowEngine
from lazerwfm.workflow_registry import WorkflowRegistry


class WorkflowInfo(BaseModel):
    """Workflow information returned by API"""

    workflow_id: str
    status: WorkflowStatus
    created_at: datetime
    result: Any | None = None
    error: str | None = None


class WorkflowList(BaseModel):
    """List of workflows with count"""

    total: int
    workflows: list[WorkflowInfo]


class WorkflowParameter(BaseModel):
    type: str
    required: bool = False
    default: Any = None
    description: str = ""


class AvailableWorkflow(BaseModel):
    name: str
    description: str
    parameters: dict[str, WorkflowParameter]
    public: bool = True


class AvailableWorkflowList(BaseModel):
    workflows: list[AvailableWorkflow]


class StartWorkflowRequest(BaseModel):
    parameters: dict[str, Any]


def create_api(engine: WorkflowEngine, registry: WorkflowRegistry) -> FastAPI:
    """Create FastAPI application with workflow engine endpoints"""
    app = FastAPI(
        title="LazerWFM API",
        description="REST API for LazerWFM workflow engine",
        version="0.1.0",
    )

    # System endpoints
    @app.get("/health", tags=["system"])
    async def health_check():
        """Check if the workflow engine is running"""
        active_workflows = len(engine._storage.get_active_workflows())
        return {
            "status": "healthy",
            "active_workflows": active_workflows,
            "engine_running": engine._running,
        }

    # Workflow listing endpoints (static paths first)
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
                        workflow_id=wf.id,
                        status=wf.status,
                        created_at=wf.created_at,
                        result=wf.get_result(),
                        error=str(wf.get_error()) if wf.get_error() else None,
                    )
                )

        return WorkflowList(total=len(workflows), workflows=workflows)

    @app.get(
        "/workflows/available", response_model=AvailableWorkflowList, tags=["workflows"]
    )
    async def list_available_workflows():
        """List available workflows that can be started"""
        workflows = []
        available = registry.list_public_workflows()

        for metadata in available:
            workflows.append(
                AvailableWorkflow(
                    name=metadata.name,
                    description=metadata.description,
                    parameters={
                        name: WorkflowParameter(**params)
                        for name, params in metadata.parameters.items()
                    },
                    public=metadata.is_public,
                )
            )
        return AvailableWorkflowList(workflows=workflows)

    # Workflow management endpoints (static paths)
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

    # Workflow instance endpoints (with path parameters)
    @app.post(
        "/workflows/start/{workflow_name}",
        response_model=WorkflowInfo,
        tags=["workflows"],
    )
    async def start_workflow(workflow_name: str, request: StartWorkflowRequest):
        """Start a workflow by name"""
        workflow_id = await engine.start_workflow_by_name(
            workflow_name, **request.parameters
        )
        workflow = engine.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return WorkflowInfo(
            workflow_id=workflow.id,
            status=workflow.status,
            created_at=workflow.created_at,
            result=workflow.get_result(),
            error=str(workflow.get_error()) if workflow.get_error() else None,
        )

    @app.get(
        "/workflows/{workflow_id}", response_model=WorkflowInfo, tags=["workflows"]
    )
    async def get_workflow(workflow_id: str):
        """Get information about a specific workflow"""
        workflow = engine.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return WorkflowInfo(
            workflow_id=workflow.id,
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

    return app
