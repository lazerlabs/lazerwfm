import asyncio
from typing import Optional, Type

import uvicorn

from lazerwfm.storage import TaskQueue, WorkflowStorage
from lazerwfm.web.api import create_api
from lazerwfm.workflow_engine import WorkflowEngine


class WorkflowServer:
    """Server that runs the workflow engine and API"""

    def __init__(
        self,
        storage: Optional[WorkflowStorage] = None,
        task_queue: Optional[TaskQueue] = None,
        host: str = "0.0.0.0",
        port: int = 8000,
    ):
        self.engine = WorkflowEngine(storage=storage, task_queue=task_queue)
        self.app = create_api(self.engine)
        self.host = host
        self.port = port

    def run(self):
        """Run the server"""
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
        )


def run_server(
    storage: Optional[WorkflowStorage] = None,
    task_queue: Optional[TaskQueue] = None,
    host: str = "0.0.0.0",
    port: int = 8000,
):
    """Helper function to run the server"""
    server = WorkflowServer(
        storage=storage, task_queue=task_queue, host=host, port=port
    )
    server.run()
