import typer
from rich.console import Console

from .app import WorkflowMonitor

app = typer.Typer(help="LazerWFM Monitor")
console = Console()


@app.command()
def monitor(
    url: str = typer.Option("http://localhost:8000", help="API base URL"),
):
    """Start the workflow monitor"""
    try:
        monitor = WorkflowMonitor(url)
        monitor.run()
    except Exception as e:
        console.print(f"[red]Error starting monitor: {e}[/red]")
