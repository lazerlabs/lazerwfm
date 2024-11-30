from __future__ import annotations

import asyncio
import uuid
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Generic, Optional, Type, TypeVar

T = TypeVar("T")

# Timeout constants (in seconds)
DEFAULT_STEP_TIMEOUT = 120  # 2 minutes
MAX_STEP_TIMEOUT = 600  # 10 minutes


class StepTransition:
    """Base class for step transitions"""

    def __init__(self, timeout: Optional[float] = None):
        if timeout is not None and timeout > MAX_STEP_TIMEOUT:
            raise ValueError(f"Step timeout cannot exceed {MAX_STEP_TIMEOUT} seconds")
        self.timeout = timeout or DEFAULT_STEP_TIMEOUT


class NextStep(StepTransition):
    """Immediate transition to the next step"""

    def __init__(self, next_step: Callable, timeout: Optional[float] = None, **params):
        super().__init__(timeout)
        self.next_step = next_step
        self.params = params


class WaitAndNextStep(NextStep):
    """Wait for specified seconds before transitioning to next step"""

    def __init__(
        self,
        wait_seconds: float,
        next_step: Callable,
        timeout: Optional[float] = None,
        **params,
    ):
        super().__init__(next_step, timeout, **params)
        self.wait_seconds = wait_seconds


class Schedule(NextStep):
    """Schedule next step at specific time"""

    def __init__(
        self,
        schedule_time: datetime,
        next_step: Callable,
        timeout: Optional[float] = None,
        **params,
    ):
        super().__init__(next_step, timeout, **params)
        self.schedule_time = schedule_time


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"
    TIMEOUT = "timeout"


class WorkflowError(Exception):
    """Base class for workflow errors"""

    pass


class StepTimeoutError(WorkflowError):
    """Raised when a step exceeds its timeout"""

    pass


class Workflow:
    """Base class for all workflows"""

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.status = WorkflowStatus.PENDING
        self._result: Any = None
        self._error: Optional[Exception] = None
        self._task_queue: deque[tuple[Callable, dict]] = deque()
        self._running_task: Optional[asyncio.Task] = None

    async def start(self, **params) -> Any:
        """Entry point for the workflow"""
        raise NotImplementedError("Workflows must implement start method")

    def get_result(self) -> Any:
        return self._result

    def set_result(self, result: Any):
        self._result = result

    def get_error(self) -> Optional[Exception]:
        return self._error

    def set_error(self, error: Exception):
        self._error = error
        self.status = WorkflowStatus.FAILED

    async def _run_workflow(self):
        """Internal method to run workflow steps"""
        self.status = WorkflowStatus.RUNNING

        while self.status == WorkflowStatus.RUNNING:
            if not self._task_queue:
                await asyncio.sleep(0.1)  # Prevent busy waiting
                continue

            current_step, params = self._task_queue.popleft()
            try:
                # Run the step with timeout
                result = await asyncio.wait_for(
                    current_step(**params), timeout=DEFAULT_STEP_TIMEOUT
                )

                if isinstance(result, NextStep):
                    if isinstance(result, WaitAndNextStep):
                        try:
                            await asyncio.wait_for(
                                asyncio.sleep(result.wait_seconds),
                                timeout=result.timeout,
                            )
                        except asyncio.TimeoutError:
                            raise StepTimeoutError(
                                f"Wait timeout after {result.timeout} seconds"
                            )

                    elif isinstance(result, Schedule):
                        now = datetime.now()
                        if result.schedule_time > now:
                            wait_seconds = (result.schedule_time - now).total_seconds()
                            try:
                                await asyncio.wait_for(
                                    asyncio.sleep(wait_seconds), timeout=result.timeout
                                )
                            except asyncio.TimeoutError:
                                raise StepTimeoutError(
                                    f"Schedule timeout after {result.timeout} seconds"
                                )

                    self._task_queue.append((result.next_step, result.params))

            except asyncio.TimeoutError:
                print(
                    f"Step {current_step.__name__} timed out after {DEFAULT_STEP_TIMEOUT} seconds"
                )
                self.set_error(
                    StepTimeoutError(f"Step {current_step.__name__} timed out")
                )
                self.status = WorkflowStatus.TIMEOUT
                break
            except Exception as e:
                print(f"Error executing step {current_step.__name__}: {e}")
                self.set_error(e)
                self.status = WorkflowStatus.FAILED
                break


class WorkflowEngine:
    """Main workflow engine that manages workflow execution"""

    def __init__(self):
        self._active_workflows: dict[str, Workflow] = {}

    async def start_workflow(self, workflow_class: Type[Workflow], **params) -> str:
        """Start a new workflow instance"""
        workflow = workflow_class()
        self._active_workflows[workflow.id] = workflow

        # Schedule the start method and begin workflow execution
        workflow._task_queue.append((workflow.start, params))
        workflow._running_task = asyncio.create_task(workflow._run_workflow())

        return workflow.id

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow instance by ID"""
        return self._active_workflows.get(workflow_id)

    async def stop_workflow(self, workflow_id: str):
        """Stop a running workflow"""
        workflow = self.get_workflow(workflow_id)
        if workflow and workflow._running_task:
            workflow._running_task.cancel()
            try:
                await workflow._running_task
            except asyncio.CancelledError:
                pass
            workflow.status = WorkflowStatus.FAILED
            workflow.set_error(WorkflowError("Workflow cancelled"))

    async def stop_all_workflows(self):
        """Stop all running workflows"""
        for workflow_id in list(self._active_workflows.keys()):
            await self.stop_workflow(workflow_id)
