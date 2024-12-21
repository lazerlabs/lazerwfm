from rich.panel import Panel
from rich.table import Table
from textual.widgets import Static


class WorkflowList(Static):
    """Widget for displaying available workflows"""

    def __init__(self):
        super().__init__()
        self.workflows = []
        self.selected_idx = 0

    def render(self) -> Panel:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Available Workflows")

        for idx, wf in enumerate(self.workflows):
            style = "reverse" if idx == self.selected_idx else ""
            table.add_row(wf["name"], style=style)

        return Panel(table, title="Available Workflows", border_style="blue")
