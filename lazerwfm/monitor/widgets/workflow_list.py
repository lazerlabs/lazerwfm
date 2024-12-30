from datetime import timedelta
from textual.containers import Vertical
from textual.widgets import DataTable, Tabs
from textual import work
import httpx
from lazerwfm.types import WorkflowStatus
from lazerwfm.web.api import WorkflowList as WFList


class WorkflowList(Vertical):
    """Widget showing the list of workflows in tabs by status."""

    DEFAULT_CSS = """
    WorkflowList {
        height: 100%;
        border: solid $primary;
        background: $surface;
    }

    Tabs {
        dock: top;
        width: 100%;
        height: 3;
    }

    DataTable {
        width: 100%;
        height: 100%;
        margin: 1;
    }
    """

    def __init__(self, api_url: str = "http://localhost:8000"):
        super().__init__()
        self.api_url = api_url
        self.current_status = WorkflowStatus.PENDING.value.upper()

    def compose(self):
        """Create tabs and content."""
        tabs = Tabs(
            WorkflowStatus.PENDING.value.upper(),
            WorkflowStatus.RUNNING.value.upper(),
            WorkflowStatus.COMPLETED.value.upper(),
            WorkflowStatus.FAILED.value.upper(),
            WorkflowStatus.WAITING.value.upper(),
            WorkflowStatus.TIMEOUT.value.upper(),
        )
        yield tabs

        # Create the table with columns
        table = DataTable()
        table.add_columns("ID", "Name", "Start Time", "Duration", "Current Step")
        yield table

    def on_mount(self):
        """Start periodic refresh when mounted."""
        self.write_log("Starting workflow monitor...")
        self.refresh_table()
        self.set_interval(5.0, self.refresh_table)  # Refresh every 5 seconds

    def refresh_table(self):
        """Refresh the table data."""
        self.write_log(f"Refreshing workflows for status: {self.current_status}")
        self.update_table_data(self.current_status)

    def _format_duration(self, seconds: float | None) -> str:
        """Format duration in seconds to a human readable string."""
        if seconds is None:
            return "0m"

        delta = timedelta(seconds=seconds)
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    async def _fetch_workflows(self, status: str) -> list[tuple]:
        """Fetch workflows from API based on status."""
        try:
            self.write_log(
                f"Fetching workflows from {self.api_url}/workflows?status={status.lower()}"
            )
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/workflows",
                    params={"status": status.lower()},
                )
                response.raise_for_status()
                data = response.json()
                workflow_list = WFList(**data)
                self.write_log(f"Found {len(workflow_list.workflows)} workflows")

                return [
                    (
                        wf.workflow_id,
                        wf.name,
                        wf.created_at.strftime("%d-%m-%Y %H:%M:%S"),
                        self._format_duration(wf.duration),
                        wf.current_step or "N/A",
                    )
                    for wf in workflow_list.workflows
                ]
        except Exception as e:
            self.write_log(f"Error fetching workflows: {e}", "red")
            return []

    @work(exclusive=True)
    async def update_table_data(self, status: str):
        """Update table data based on status."""
        table = self.query_one(DataTable)
        rows = await self._fetch_workflows(status)
        table.clear()
        table.add_rows(rows)

    def on_tabs_tab_activated(self, event: Tabs.TabActivated):
        """Handle tab changes."""
        self.current_status = event.tab.label
        self.write_log(f"Switched to tab: {self.current_status}")
        self.refresh_table()

    def write_log(self, message: str, style: str = "white"):
        """Write a message to the log screen."""
        if self.app.is_screen_installed("logs"):
            log_screen = self.app.get_screen("logs")
            log_screen.write_log(message, style)
