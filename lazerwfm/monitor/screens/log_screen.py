from datetime import datetime
from textual.screen import Screen
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Log
from textual.css.query import NoMatches
from textual.app import ComposeResult


class LogScreen(Screen):
    """A full screen view of application logs."""

    BINDINGS = [
        Binding("m", "switch_to_main", "Main Screen", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    DEFAULT_CSS = """
    LogScreen {
        background: $surface;
    }

    Log {
        width: 100%;
        height: auto;
        background: $surface;
        color: $text;
        border: solid $primary;
        padding: 1;
        overflow-y: scroll;
    }

    Header {
        background: $surface;
    }

    Footer {
        background: $surface;
    }
    """

    def __init__(self):
        super().__init__()
        self._pending_messages = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header("Application Logs")
        yield Log()
        yield Footer()

    def on_mount(self):
        """Handle any pending messages once the screen is mounted."""
        log_widget = self.query_one(Log)
        # Add a test message to verify logging works
        self.write_log("Log screen initialized", "green")
        for message, style in self._pending_messages:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_widget.write(f"[{timestamp}] [{style}]{message}")
        self._pending_messages.clear()

    def write_log(self, message: str, style: str = "white"):
        """Add a log message with optional style."""
        try:
            log_widget = self.query_one(Log)
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] [{style}]{message}[/]\n"
            log_widget.write(formatted_message)
            log_widget.scroll_end(animate=False)
        except NoMatches:
            # Store message for later if Log widget isn't available yet
            self._pending_messages.append((message, style))

    def action_switch_to_main(self):
        """Switch back to the main screen."""
        self.app.push_screen("main")
