import asyncio
import random
from datetime import datetime, timedelta

from workflow_engine import (
    DEFAULT_STEP_TIMEOUT,
    MAX_STEP_TIMEOUT,
    NextStep,
    Schedule,
    StepTimeoutError,
    Workflow,
    WorkflowEngine,
    WorkflowStatus,
)


class LongRunningWorkflow(Workflow):
    async def start(self, sleep_time: float = DEFAULT_STEP_TIMEOUT + 10) -> NextStep:
        print(f"Starting long running workflow, will sleep for {sleep_time} seconds")
        # This will exceed the default timeout
        await asyncio.sleep(sleep_time)
        return NextStep(self.complete)

    async def complete(self) -> None:
        print("This should not be reached due to timeout")
        self.status = WorkflowStatus.COMPLETED


class CustomTimeoutWorkflow(Workflow):
    async def start(self, sleep_time: float = 5) -> NextStep:
        print(f"Starting workflow with custom timeout: {sleep_time} seconds")
        return NextStep(self.long_step, timeout=10.0, sleep_time=sleep_time)

    async def long_step(self, sleep_time: float) -> None:
        print(f"Running long step for {sleep_time} seconds")
        await asyncio.sleep(sleep_time)
        print("Long step completed")
        self.status = WorkflowStatus.COMPLETED


class ParallelWorkflow(Workflow):
    async def start(self, name: str) -> NextStep:
        print(f"{self.__class__.__name__} Starting with name: {name}")
        return NextStep(self.repeat_step, repetitions=5, name=name)

    async def repeat_step(self, repetitions: int, name: str) -> NextStep:
        print(f"{self.__class__.__name__}:{name} Repeating step {repetitions} times")
        await asyncio.sleep(random.randint(1, 10))
        if repetitions > 1:
            return NextStep(self.repeat_step, repetitions=repetitions - 1, name=name)
        else:
            return NextStep(self.complete, name=name)

    async def complete(self, name: str) -> None:
        print(f"{self.__class__.__name__}:{name} Completed")
        self.status = WorkflowStatus.COMPLETED


async def main():
    engine = WorkflowEngine()

    # print("\nTesting workflow that exceeds default timeout:")
    # workflow_id = await engine.start_workflow(LongRunningWorkflow)
    # while True:
    #    workflow = engine.get_workflow(workflow_id)
    #    if workflow.status in (
    #        WorkflowStatus.COMPLETED,
    #        WorkflowStatus.FAILED,
    #        WorkflowStatus.TIMEOUT,
    #    ):
    #        print(f"Workflow status: {workflow.status}")
    #        if workflow.get_error():
    #            print(f"Error: {workflow.get_error()}")
    #        break
    #    await asyncio.sleep(0.1)
    #
    # print("\nTesting workflow with custom timeout (should complete):")
    # workflow_id = await engine.start_workflow(CustomTimeoutWorkflow, sleep_time=5)
    #
    # while True:
    #    workflow = engine.get_workflow(workflow_id)
    #    if workflow.status in (
    #        WorkflowStatus.COMPLETED,
    #        WorkflowStatus.FAILED,
    #        WorkflowStatus.TIMEOUT,
    #    ):
    #        print(f"Workflow status: {workflow.status}")
    #        if workflow.get_error():
    #            print(f"Error: {workflow.get_error()}")
    #        break
    #    await asyncio.sleep(0.1)

    print("\nTesting parallel workflows:")
    workflow_id1 = await engine.start_workflow(ParallelWorkflow, name="Workflow 1")
    workflow_id2 = await engine.start_workflow(ParallelWorkflow, name="Workflow 2")

    while True:
        workflow1 = engine.get_workflow(workflow_id1)
        workflow2 = engine.get_workflow(workflow_id2)
        if (
            workflow1.status == WorkflowStatus.COMPLETED
            and workflow2.status == WorkflowStatus.COMPLETED
        ):
            print("Both parallel workflows completed")
            break
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
