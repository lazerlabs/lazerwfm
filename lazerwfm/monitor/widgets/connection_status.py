from textual.reactive import reactive
from textual.widgets import Static


class ConnectionStatus(Static):
    """Widget showing the connection status to the workflow engine."""

    DEFAULT_CSS = """
    ConnectionStatus {
        height: 3;
        content-align: center middle;
        background: $boost;
    }

    ConnectionStatus.-connected {
        color: $success;
    }

    ConnectionStatus.-disconnected {
        color: $error;
    }
    """

    is_connected = reactive(False)
    status_message = reactive("")

    def __init__(self):
        super().__init__("")
        self.update_status(False, "Initializing...")

    def update_status(self, connected: bool, message: str = ""):
        """Update the connection status and message."""
        self.is_connected = connected
        self.status_message = message
        self._update_display()

    def _update_display(self):
        """Update the display based on connection status."""
        icon = "🟢" if self.is_connected else "🔴"
        self.update(f"{icon} {self.status_message}")
        self.set_class(self.is_connected, "-connected")
        self.set_class(not self.is_connected, "-disconnected")
