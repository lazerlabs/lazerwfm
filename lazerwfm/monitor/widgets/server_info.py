from rich.panel import Panel
from rich.table import Table
from textual.widgets import Static


class ServerInfo(Static):
    """Widget for displaying server information"""

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.active_workflows = 0

    def render(self) -> Panel:
        grid = Table.grid(padding=1)
        grid.add_column("Label", style="bold")
        grid.add_column("Value")

        grid.add_row("Server:", self.url)
        grid.add_row("Status:", "[green]Connected[/green]")
        grid.add_row("Active Workflows:", str(self.active_workflows))

        return Panel(grid, title="Server Information", border_style="green")
