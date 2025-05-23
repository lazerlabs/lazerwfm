from datetime import datetime
from typing import Any

import httpx
import typer
from httpx import ConnectError
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

app = typer.Typer(help="LazerWFM CLI")
console = Console()


class WorkflowClient:
    """Client for interacting with LazerWFM API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def list_workflows(self) -> dict:
        """List all workflows"""
        response = await self.client.get("/workflows")
        response.raise_for_status()
        return response.json()

    async def get_workflow(self, workflow_id: str) -> dict:
        """Get workflow details"""
        response = await self.client.get(f"/workflows/{workflow_id}")
        response.raise_for_status()
        return response.json()

    async def stop_workflow(self, workflow_id: str) -> dict:
        """Stop a workflow"""
        response = await self.client.post(f"/workflows/{workflow_id}/stop")
        response.raise_for_status()
        return response.json()

    async def stop_all_workflows(self) -> dict:
        """Stop all workflows"""
        response = await self.client.post("/workflows/stop-all")
        response.raise_for_status()
        return response.json()

    async def cleanup_workflows(self, before: datetime) -> dict:
        """Clean up old workflows"""
        response = await self.client.post(
            "/workflows/cleanup", json={"before": before.isoformat()}
        )
        response.raise_for_status()
        return response.json()

    async def get_health(self) -> dict:
        """Get system health"""
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the client session"""
        await self.client.aclose()

    async def list_available_workflows(self) -> dict:
        """List available workflows"""
        response = await self.client.get("/workflows/available")
        response.raise_for_status()
        return response.json()

    async def start_workflow(self, workflow_name: str, params: dict[str, Any]) -> dict:
        """Start a workflow by name"""
        response = await self.client.post(
            f"/workflows/start/{workflow_name}", json={"parameters": params}
        )
        response.raise_for_status()
        return response.json()


def create_workflow_table(workflows: list[dict]) -> Table:
    """Create a rich table for workflows"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Status")
    table.add_column("Created At")
    table.add_column("Result")
    table.add_column("Error")

    for wf in workflows:
        table.add_row(
            wf["workflow_id"],
            wf["status"],
            wf["created_at"],
            str(wf["result"]) if wf["result"] else "",
            wf["error"] or "",
        )

    return table


@app.command()
def list_workflows(
    url: str = typer.Option("http://localhost:8000", help="API base URL"),
):
    """List all workflows"""

    async def _list():
        client = WorkflowClient(url)
        try:
            with Progress() as progress:
                task = progress.add_task("Fetching workflows...", total=1)
                result = await client.list_workflows()
                progress.update(task, advance=1)

            table = create_workflow_table(result["workflows"])
            console.print(table)
            console.print(f"\nTotal workflows: {result['total']}")
        finally:
            await client.close()

    import asyncio

    asyncio.run(_list())


@app.command()
def get_workflow(
    workflow_id: str,
    url: str = typer.Option("http://localhost:8000", help="API base URL"),
):
    """Get workflow details"""

    async def _get():
        client = WorkflowClient(url)
        try:
            with Progress() as progress:
                task = progress.add_task("Fetching workflow...", total=1)
                result = await client.get_workflow(workflow_id)
                progress.update(task, advance=1)

            table = create_workflow_table([result])
            console.print(table)
        finally:
            await client.close()

    import asyncio

    asyncio.run(_get())


@app.command()
def stop_workflow(
    workflow_id: str,
    url: str = typer.Option("http://localhost:8000", help="API base URL"),
):
    """Stop a workflow"""

    async def _stop():
        client = WorkflowClient(url)
        try:
            with Progress() as progress:
                task = progress.add_task("Stopping workflow...", total=1)
                result = await client.stop_workflow(workflow_id)
                progress.update(task, advance=1)

            console.print(f"[green]Workflow stopped: {result['status']}[/green]")
        finally:
            await client.close()

    import asyncio

    asyncio.run(_stop())


@app.command()
def stop_all():
    """Stop all workflows"""

    async def _stop_all():
        client = WorkflowClient()
        try:
            with Progress() as progress:
                task = progress.add_task("Stopping all workflows...", total=1)
                result = await client.stop_all_workflows()
                progress.update(task, advance=1)

            console.print(f"[green]{result['status']}[/green]")
        finally:
            await client.close()

    import asyncio

    asyncio.run(_stop_all())


@app.command()
def health():
    """Check system health"""

    async def _health():
        client = WorkflowClient()
        try:
            result = await client.get_health()
            console.print("\n[bold]System Health[/bold]")
            console.print(f"Status: [green]{result['status']}[/green]")
            console.print(f"Active Workflows: {result['active_workflows']}")
            console.print(f"Engine Running: {result['engine_running']}")
        finally:
            await client.close()

    import asyncio

    asyncio.run(_health())


@app.command()
def list_available():
    """List available workflows"""

    async def _list():
        client = WorkflowClient()
        try:
            with Progress() as progress:
                task = progress.add_task("Fetching available workflows...", total=1)
                try:
                    result = await client.list_available_workflows()
                except ConnectError:
                    console.print(
                        "[red]Error: Could not connect to server. Is the server running?[/red]"
                    )
                    return
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")
                    return
                progress.update(task, advance=1)

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name")
            table.add_column("Description")
            table.add_column("Parameters")

            for wf in result["workflows"]:
                params = ", ".join(
                    f"{k}{'*' if v.get('required') else ''}"
                    for k, v in wf["parameters"].items()
                )
                table.add_row(wf["name"], wf["description"], params)

            console.print(table)
        finally:
            await client.close()

    import asyncio

    asyncio.run(_list())


@app.command()
def start(
    workflow_name: str,
    params: list[str] = typer.Option(
        [], "--param", "-p", help="Parameters in key=value format"
    ),
    url: str = typer.Option("http://localhost:8000", help="API base URL"),
):
    """Start a workflow"""
    workflow_params = {}
    for param in params:
        try:
            key, value = param.split("=", 1)
            workflow_params[key.strip()] = value.strip()
        except ValueError:
            console.print(f"[red]Invalid parameter format: {param}[/red]")
            return

    async def _start():
        client = WorkflowClient(url)
        try:
            with Progress() as progress:
                task = progress.add_task("Starting workflow...", total=1)
                result = await client.start_workflow(workflow_name, workflow_params)
                progress.update(task, advance=1)

            console.print(f"[green]Workflow started: {result['workflow_id']}[/green]")
        finally:
            await client.close()

    import asyncio

    asyncio.run(_start())


def run_cli():
    """Run the CLI application"""
    app()
