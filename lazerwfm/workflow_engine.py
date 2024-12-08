from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Type

from .storage import (
    MemoryTaskQueue,
    MemoryWorkflowStorage,
    TaskQueue,
    WorkflowStorage,
)
from .types import (
    DEFAULT_STEP_TIMEOUT,
    NextStep,
    StepTransition,
    Schedule,
    StepTimeoutError,
    WaitAndNextStep,
    WorkflowError,
    WorkflowStatus,
    TransitionType,
)
from .workflow import Workflow


class WorkflowEngine:
    """Main workflow engine that manages workflow execution"""

    def __init__(
        self,
        storage: WorkflowStorage | None = None,
        task_queue: TaskQueue | None = None,
    ):
        self._storage = (
            storage or MemoryWorkflowStorage()
        )  # If not specified, defaults to in-memory storage
        self._task_queue = (
            task_queue or MemoryTaskQueue()
        )  # If not specified, defaults to in-memory task queue
        self._running = False
        self._engine_task: asyncio.Task | None = None

    async def start_workflow(self, workflow_class: Type[Workflow], **params) -> str:
        """Start a new workflow instance"""
        workflow = workflow_class()
        self._storage.add_workflow(workflow)
        workflow.status = WorkflowStatus.RUNNING

        # Schedule the start method
        self._task_queue.push(workflow.id, "start", params)

        if not self._running:
            self._engine_task = asyncio.create_task(self._run_engine())
            self._running = True

        return workflow.id

    async def _run_engine(self):
        """Main engine loop"""
        self._running = True

        while self._running:
            task = self._task_queue.pop()
            if not task:
                await asyncio.sleep(0.1)  # Prevent busy waiting
                continue

            workflow_id, step_name, params = task
            workflow = self._storage.get_workflow(workflow_id)
            if not workflow:
                continue

            try:
                step_method = getattr(workflow, step_name)
                result = await asyncio.wait_for(
                    step_method(**params), timeout=DEFAULT_STEP_TIMEOUT
                )

                if isinstance(result, StepTransition):
                    match result.transition_type:
                        case "WAIT_AND_NEXT":
                            try:
                                await asyncio.wait_for(
                                    asyncio.sleep(result.wait_seconds),
                                    timeout=result.timeout,
                                )
                            except asyncio.TimeoutError:
                                raise StepTimeoutError(
                                    f"Wait timeout after {result.timeout} seconds"
                                )

                        case "SCHEDULE":
                            now = datetime.now()
                            if result.schedule_time > now:
                                wait_seconds = (
                                    result.schedule_time - now
                                ).total_seconds()
                                try:
                                    await asyncio.wait_for(
                                        asyncio.sleep(wait_seconds),
                                        timeout=result.timeout,
                                    )
                                except asyncio.TimeoutError:
                                    raise StepTimeoutError(
                                        f"Schedule timeout after {result.timeout} seconds"
                                    )

                        case "NEXT_STEP":
                            pass  # Immediate transition, no waiting needed

                # Schedule next step
                self._task_queue.push(
                    workflow_id, result.next_step.__name__, result.params
                )
            except asyncio.TimeoutError:
                print(
                    f"Step {step_name} timed out after {DEFAULT_STEP_TIMEOUT} seconds"
                )
                workflow.set_error(StepTimeoutError(f"Step {step_name} timed out"))
                workflow.status = WorkflowStatus.TIMEOUT
            except Exception as e:
                print(f"Error executing step {step_name}: {e}")
                workflow.set_error(e)
                workflow.status = WorkflowStatus.FAILED

            # Check if workflow should be moved to cold storage
            if workflow.status in (
                WorkflowStatus.COMPLETED,
                WorkflowStatus.FAILED,
                WorkflowStatus.TIMEOUT,
            ):
                self._storage.move_to_cold_storage(workflow_id)

    def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Get workflow instance by ID"""
        return self._storage.get_workflow(workflow_id)

    async def stop_workflow(self, workflow_id: str):
        """Stop a running workflow"""
        workflow = self.get_workflow(workflow_id)
        if workflow and workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.FAILED
            workflow.set_error(WorkflowError("Workflow cancelled"))
            self._storage.move_to_cold_storage(workflow_id)

    async def stop_all_workflows(self):
        """Stop all running workflows"""
        for workflow_id in self._storage.get_active_workflows():
            await self.stop_workflow(workflow_id)

    async def cleanup_old_workflows(self, before: datetime):
        """Clean up workflows from cold storage older than the specified date"""
        self._storage.cleanup_cold_storage(before)
