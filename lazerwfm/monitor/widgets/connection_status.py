from textual.widgets import Static


class ConnectionStatus(Static):
    """Widget showing the connection status to the workflow engine."""

    DEFAULT_CSS = """
    ConnectionStatus {
        height: 3;
        content-align: center middle;
        background: $boost;
        color: $success;
    }
    """

    def __init__(self):
        super().__init__("🟢 Lorem ipsum dolor sit amet - Connected to Engine XYZ")
