from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

# Timeout constants (in seconds)
DEFAULT_STEP_TIMEOUT = 120  # 2 minutes
MAX_STEP_TIMEOUT = 600  # 10 minutes


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


class StepTransition:
    """Base class for step transitions"""

    def __init__(self, timeout: float | None = None):
        if timeout is not None and timeout > MAX_STEP_TIMEOUT:
            raise ValueError(f"Step timeout cannot exceed {MAX_STEP_TIMEOUT} seconds")
        self.timeout = timeout or DEFAULT_STEP_TIMEOUT


class NextStep(StepTransition):
    """Immediate transition to the next step"""

    def __init__(self, next_step: Callable, timeout: float | None = None, **params):
        super().__init__(timeout)
        self.next_step = next_step
        self.params = params


class WaitAndNextStep(NextStep):
    """Wait for specified seconds before transitioning to next step"""

    def __init__(
        self,
        wait_seconds: float,
        next_step: Callable,
        timeout: float | None = None,
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
        timeout: float | None = None,
        **params,
    ):
        super().__init__(next_step, timeout, **params)
        self.schedule_time = schedule_time
