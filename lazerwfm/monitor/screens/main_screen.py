from textual.screen import Screen
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Header, Footer, Placeholder
from ..widgets import ConnectionStatus, WorkflowList


class MainScreen(Screen):
    """The main application screen."""

    BINDINGS = [
        Binding("l", "switch_to_logs", "View Logs", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("h", "help", "Help", show=True),
    ]

    def compose(self):
        """Create child widgets for the screen."""
        yield Header()

        # Main content container
        with Container():
            # Status bar
            yield ConnectionStatus()

            # Two-column layout
            with Container():
                # Left column
                yield Placeholder("Workflow Tree", id="tree")
                # Right column
                with Container(id="right-pane"):
                    yield WorkflowList()

        yield Footer()

    def action_switch_to_logs(self):
        """Switch to the logs screen."""
        self.app.push_screen("logs")

    def action_refresh(self):
        """Handle refresh key press."""
        workflow_list = self.query_one(WorkflowList)
        workflow_list.refresh_table()
