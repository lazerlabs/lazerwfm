from __future__ import annotations

import asyncio

from textual.app import App
from textual.containers import Container
from textual.widgets import Footer, Header

from ..cli.client import WorkflowClient
from .widgets import ServerInfo, StatusView, WorkflowList


class WorkflowMonitor(App):
    """TUI application for monitoring workflows"""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("up", "cursor_up", "Move up"),
        ("down", "cursor_down", "Move down"),
        ("enter", "select", "Select"),
    ]

    def __init__(self, url: str = "http://localhost:8000"):
        super().__init__()
        self.url = url
        self.client = WorkflowClient(url)

        # Create widgets
        self.workflow_list = WorkflowList()
        self.status_view = StatusView()
        self.server_info = ServerInfo(url)

    def compose(self):
        """Create and compose the UI elements"""
        yield Header()

        with Container():
            with Container(id="main-content"):
                yield self.workflow_list
                yield self.status_view
            yield self.server_info

        yield Footer()

    async def on_mount(self) -> None:
        """Set up periodic refresh"""
        # Set up CSS styling
        self.main_container = self.query_one("#main-content")
        self.main_container.styles.layout = "horizontal"
        self.main_container.styles.height = "100%"

        # Start refresh loop
        self.refresh_task = asyncio.create_task(self.refresh_loop())

    async def refresh_loop(self):
        """Periodically refresh data"""
        while True:
            await self.refresh_data()
            await asyncio.sleep(2)  # Refresh every 2 seconds

    async def refresh_data(self):
        """Refresh workflow data"""
        try:
            # Get available workflows
            available = await self.client.list_available_workflows()
            self.workflow_list.workflows = available["workflows"]
            self.workflow_list.refresh()

            # Get running workflows
            workflows = await self.client.list_workflows()
            self.status_view.workflows = workflows["workflows"]
            self.status_view.refresh()

            # Update server info
            self.server_info.active_workflows = len(workflows["workflows"])
            self.server_info.refresh()

        except Exception as e:
            # Handle errors gracefully
            self.log(f"Error refreshing data: {e}")

    def action_cursor_up(self):
        """Move cursor up in workflow list"""
        if self.workflow_list.workflows:
            self.workflow_list.selected_idx = (
                self.workflow_list.selected_idx - 1
            ) % len(self.workflow_list.workflows)
            self.workflow_list.refresh()

    def action_cursor_down(self):
        """Move cursor down in workflow list"""
        if self.workflow_list.workflows:
            self.workflow_list.selected_idx = (
                self.workflow_list.selected_idx + 1
            ) % len(self.workflow_list.workflows)
            self.workflow_list.refresh()

    async def action_select(self):
        """Toggle selected status group"""
        if self.workflow_list.workflows:
            selected = self.workflow_list.workflows[self.workflow_list.selected_idx]
            self.status_view.status_tree.toggle_status(selected["name"])
            self.status_view.refresh()
