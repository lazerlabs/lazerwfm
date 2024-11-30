# LazerWFM

A flexible async workflow manager that supports parallel execution, timeouts, and complex workflow patterns.

## Features

- Fully async workflow execution
- Parallel workflow support
- Configurable timeouts
- Step transitions (NextStep, WaitAndNextStep, Schedule)
- Workflow status tracking
- Error handling and timeout management

## Installation

```bash
pip install lazerwfm
```

## Quick Start

```python
import asyncio
from lazerwfm import Workflow, NextStep, WorkflowEngine

class MyWorkflow(Workflow):
    async def start(self, name: str) -> NextStep:
        print(f"Starting workflow: {name}")
        return NextStep(self.step2, value=42)
    
    async def step2(self, value: int) -> None:
        print(f"Processing value: {value}")
        self.status = WorkflowStatus.COMPLETED

async def main():
    engine = WorkflowEngine()
    workflow_id = await engine.start_workflow(MyWorkflow, name="test")
    
    # Wait for completion
    while True:
        workflow = engine.get_workflow(workflow_id)
        if workflow.status == WorkflowStatus.COMPLETED:
            break
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
```

## License

MIT License 