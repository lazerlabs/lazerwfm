from datetime import datetime
from typing import Any

from rich.panel import Panel
from rich.tree import Tree
from textual.widgets import Static


class WorkflowStatusTree:
    """Tree view of workflows grouped by status"""

    def __init__(self):
        self.tree = Tree("Workflow Status")
        self.status_nodes = {}
        self.expanded_status = None

    def update(self, workflows: list[dict[str, Any]]) -> Tree:
        """Update the tree with current workflow data"""
        # Group workflows by status
        by_status = {}
        for wf in workflows:
            status = wf["status"]
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(wf)

        # Clear and rebuild tree
        self.tree = Tree("[bold]Workflow Status[/bold]")

        # Sort statuses for consistent display
        for status in sorted(by_status.keys()):
            wfs = by_status[status]
            status_node = self.tree.add(
                f"[bold]{status}[/bold] ({len(wfs)})",
                guide_style="bold cyan",
            )
            self.status_nodes[status] = status_node

            # Show workflows if status is expanded
            if status == self.expanded_status:
                for wf in sorted(wfs, key=lambda x: x["created_at"], reverse=True):
                    created = datetime.fromisoformat(wf["created_at"])
                    details = [
                        f"[bold blue]ID:[/bold blue] {wf['workflow_id']}",
                        f"[bold green]Created:[/bold green] {created.strftime('%Y-%m-%d %H:%M:%S')}",
                    ]
                    if wf["result"]:
                        details.append(
                            f"[bold yellow]Result:[/bold yellow] {wf['result']}"
                        )
                    if wf["error"]:
                        details.append(f"[bold red]Error:[/bold red] {wf['error']}")

                    status_node.add("\n".join(details))

        return self.tree

    def toggle_status(self, status: str):
        """Toggle expansion of a status group"""
        if self.expanded_status == status:
            self.expanded_status = None
        else:
            self.expanded_status = status


class StatusView(Static):
    """Widget for displaying workflow status tree"""

    def __init__(self):
        super().__init__()
        self.status_tree = WorkflowStatusTree()
        self.workflows = []

    def render(self) -> Panel:
        # Update the tree with current workflows
        tree = self.status_tree.update(self.workflows)

        # If no workflows, show a message
        if not self.workflows:
            content = "[dim]No workflows running[/dim]"
        else:
            content = tree

        return Panel(
            content,
            title="Workflow Status",
            border_style="cyan",
        )
