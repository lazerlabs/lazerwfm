import asyncio
import random
from datetime import datetime, timedelta

from lazerwfm import (
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
    async def start(self, name: str, sleep_time: float = 0) -> NextStep:
        print(f"{self.__class__.__name__} Starting with name: {name}")
        return NextStep(
            self.repeat_step, repetitions=3, name=name, sleep_time=sleep_time
        )

    async def repeat_step(
        self, repetitions: int, name: str, sleep_time: float
    ) -> NextStep:
        print(f"{self.__class__.__name__}:{name} Repeating step {repetitions} times")
        await asyncio.sleep(sleep_time)
        if repetitions > 1:
            return NextStep(
                self.repeat_step,
                repetitions=repetitions - 1,
                name=name,
                sleep_time=sleep_time,
            )
        else:
            return NextStep(self.complete, name=name)

    async def complete(self, name: str) -> None:
        print(f"{self.__class__.__name__}:{name} Completed")
        self.status = WorkflowStatus.COMPLETED


async def main():
    engine = WorkflowEngine()

    print("\nTesting parallel workflows:")
    # Start initial 3 workflows
    initial_workflows = [
        ("Workflow 1", 0.5),
        ("Workflow 2", 0.3),
        ("Workflow 3", 0.2),
    ]

    for name, sleep_time in initial_workflows:
        await engine.start_workflow(ParallelWorkflow, name=name, sleep_time=sleep_time)
        await asyncio.sleep(0.1)  # Small delay between starts

    # Additional workflows to add while running
    additional_workflows = [
        ("Workflow 4", 0.4),
        ("Workflow 5", 0.3),
        ("Workflow 6", 0.2),
    ]

    added_count = 0
    while True:
        # Add new workflow if there are any left
        if added_count < len(additional_workflows):
            name, sleep_time = additional_workflows[added_count]
            await engine.start_workflow(
                ParallelWorkflow, name=name, sleep_time=sleep_time
            )
            added_count += 1
            print(f"Added new workflow: {name}")

        await asyncio.sleep(0.1)
        active_workflow_ids = engine._storage.get_active_workflows()
        active_workflows = [engine.get_workflow(wf_id) for wf_id in active_workflow_ids]
        print(f"Active workflows: {len(active_workflows)}")

        if not active_workflows and added_count >= len(additional_workflows):
            print("All workflows completed")
            break

        if all(
            wf.status == WorkflowStatus.COMPLETED for wf in active_workflows
        ) and added_count >= len(additional_workflows):
            print("All workflows completed")
            break

    await engine.stop_all_workflows()


if __name__ == "__main__":
    asyncio.run(main())
