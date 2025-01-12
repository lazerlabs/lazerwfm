from textual.app import App

from lazerwfm.monitor.screens import LogScreen, MainScreen


class WorkflowMonitor(App):
    """A TUI application to monitor workflow status."""

    CSS = """
    Container {
        height: 100%;
        width: 100%;
    }

    Container > Container {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
    }

    #right-pane {
        layout: grid;
        grid-size: 1;
        grid-rows: 1fr;
    }

    """

    SCREENS = {
        "main": MainScreen,
        "logs": LogScreen,
    }

    def on_mount(self):
        """Handle app mount event."""
        self.push_screen("main")


def main():
    app = WorkflowMonitor()
    app.run()


if __name__ == "__main__":
    main()
