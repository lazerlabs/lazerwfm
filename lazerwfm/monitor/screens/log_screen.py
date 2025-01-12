from collections.abc import Container
from datetime import datetime

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Footer, Header, Log, RichLog


class LogScreen(Screen):
    """A full screen view of application logs."""

    BINDINGS = [
        Binding("m", "switch_to_main", "Main Screen", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    DEFAULT_CSS = """
        Container {
            width: 100%;
            height: 100%;
            overflow-y: auto;
        }

        RichLog {
            width: 100%;
            height: 100%;
            background: $surface;
            color: $text;
            border: solid $primary;
            padding: 1;
            overflow: auto;
        }

        Header {
            dock: top;
            background: $surface;
        }

        Footer {
            dock: bottom;
            background: $surface;
        }
    """

    def __init__(self):
        super().__init__()
        self._pending_messages = []

    def compose(self) -> ComposeResult:
        """Create child widgets for the screen."""
        yield Header("Application Logs")
        # Main content container
        with Container():
            yield RichLog(highlight=True, markup=True)
        yield Footer()

    def on_mount(self):
        """Handle any pending messages once the screen is mounted."""
        log_widget = self.query_one(RichLog)
        # Add a test message to verify logging works
        self.write_log("Log screen initialized", "green")
        for message, style in self._pending_messages:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_widget.write(f"[{timestamp}] [{style}]{message}[/]")
        self._pending_messages.clear()

    def write_log(self, message: str, style: str = "white"):
        """Add a log message with optional style."""
        try:
            log_widget = self.query_one(RichLog)
            timestamp = datetime.now().strftime("%H:%M:%S")
            # Use simple Rich color syntax without parentheses
            formatted_message = f"[{timestamp}] [{style}]{message}[/]"
            log_widget.write(formatted_message)
            log_widget.scroll_end(animate=False)
        except NoMatches:
            # Store message for later if Log widget isn't available yet
            self._pending_messages.append((message, style))

    def action_switch_to_main(self):
        """Switch back to the main screen."""
        self.app.push_screen("main")
