# LazerWFM

A flexible async workflow manager that supports parallel execution, timeouts, and complex workflow patterns.

## Features

- Fully async workflow execution
- Parallel workflow support
- Configurable timeouts (default: 2 mins, max: 10 mins)
- Step transitions (NextStep, WaitAndNextStep, Schedule)
- Workflow status tracking
- Error handling and timeout management
- REST API with FastAPI
- CLI with rich interface

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install package
pip install -e .
```

## Usage

### As a Python Library

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

### Using the REST API

Start the server:
```bash
lazerwfm-server
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs

### Using the CLI

```bash
# List workflows
lazerwfm list-workflows

# Get workflow details
lazerwfm get-workflow <id>

# Stop workflow
lazerwfm stop-workflow <id>

# Stop all workflows
lazerwfm stop-all

# Check system health
lazerwfm health
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run server in development mode
uvicorn lazerwfm.web.server:app --reload
```

## License

MIT License 