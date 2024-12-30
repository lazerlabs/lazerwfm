import asyncio
import os
from pathlib import Path
from typing import Optional, Type

import uvicorn
from rich.console import Console
from rich.table import Table

from lazerwfm.storage import TaskQueue, WorkflowStorage
from lazerwfm.web.api import create_api
from lazerwfm.workflow_engine import WorkflowEngine
from lazerwfm.workflow_registry import WorkflowRegistry


class WorkflowServer:
    """Server that runs the workflow engine and API"""

    def __init__(
        self,
        engine: Optional[WorkflowEngine] = None,
        registry: Optional[WorkflowRegistry] = None,
        storage: Optional[WorkflowStorage] = None,
        task_queue: Optional[TaskQueue] = None,
        host: str = "0.0.0.0",
        port: int = 8000,
        config_path: Optional[str | Path] = None,
    ):
        self.registry = registry or WorkflowRegistry()

        # Load workflows from config if path provided or try to find it
        if config_path:
            self.registry.load_from_config(config_path)
        else:
            # Try to find workflows.yml in current directory or parent directories
            current_dir = Path.cwd()
            config_file = current_dir / "workflows.yml"
            if config_file.exists():
                self.registry.load_from_config(config_file)
            else:
                parent_dir = current_dir.parent
                config_file = parent_dir / "workflows.yml"
                if config_file.exists():
                    self.registry.load_from_config(config_file)

        self.engine = engine or WorkflowEngine(
            storage=storage, task_queue=task_queue, registry=self.registry
        )
        self.app = create_api(self.engine, self.registry)
        self.host = host
        self.port = port
        self.console = Console()

    def print_endpoints(self):
        """Print available API endpoints in a formatted table"""
        table = Table(title="Available API Endpoints", show_header=True)
        table.add_column("Method", style="cyan")
        table.add_column("Path", style="green")
        table.add_column("Description", style="yellow")

        # Sort routes by path for consistent display
        routes = sorted(self.app.routes, key=lambda x: x.path)

        for route in routes:
            # Skip OpenAPI endpoints
            if route.path in ["/openapi.json", "/docs", "/redoc"]:
                continue

            methods = [method for method in route.methods if method != "HEAD"]
            method_str = ", ".join(methods)

            # Get description from the endpoint's docstring
            description = ""
            if hasattr(route, "endpoint") and route.endpoint.__doc__:
                description = route.endpoint.__doc__.strip()
                # Truncate long descriptions
                if len(description) > 50:
                    description = description[:47] + "..."

            table.add_row(method_str, route.path, description)

        self.console.print("\n")
        self.console.print(table)
        self.console.print(
            "\n[blue]API Documentation available at:[/blue]"
            f"\n- Swagger UI: http://{self.host}:{self.port}/docs"
            f"\n- ReDoc: http://{self.host}:{self.port}/redoc\n"
        )

    def run(self):
        """Run the server"""
        self.print_endpoints()
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
        )


def run_server(
    engine: Optional[WorkflowEngine] = None,
    registry: Optional[WorkflowRegistry] = None,
    storage: Optional[WorkflowStorage] = None,
    task_queue: Optional[TaskQueue] = None,
    host: str = "0.0.0.0",
    port: int = 8000,
    config_path: Optional[str | Path] = None,
):
    """Helper function to run the server"""
    server = WorkflowServer(
        engine=engine,
        registry=registry,
        storage=storage,
        task_queue=task_queue,
        host=host,
        port=port,
        config_path=config_path,
    )
    server.run()
