"""Ghost Sentry Operator Console."""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, RichLog, Static
from textual.containers import Horizontal, Vertical
import json
from pathlib import Path

CSS = """
#tracks-container {
    width: 55%;
    height: 100%;
}

#logs-container {
    width: 45%;
    height: 100%;
    border-left: solid green;
}

#tracks {
    height: 100%;
}

#logs {
    height: 100%;
}

.title {
    background: $accent;
    text-align: center;
    padding: 0 1;
}
"""

class SentryConsole(App):
    """The Ghost Sentry operator console."""
    
    CSS = CSS
    BINDINGS = [("q", "quit", "Quit"), ("r", "refresh", "Refresh"), ("c", "clear", "Clear")]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                Static("📡 Detected Tracks", classes="title"),
                DataTable(id="tracks"),
                id="tracks-container"
            ),
            Vertical(
                Static("🎯 Cueing Tasks", classes="title"),
                RichLog(id="logs", markup=True),
                id="logs-container"
            ),
        )
        yield Footer()
    
    def on_mount(self) -> None:
        table = self.query_one("#tracks", DataTable)
        table.add_columns("ID", "Type", "Conf", "Lat", "Lon")
        self.load_tracks()
    
    def load_tracks(self) -> None:
        table = self.query_one("#tracks", DataTable)
        table.clear()
        
        log_widget = self.query_one("#logs", RichLog)
        log_widget.clear()
        
        log = Path("lattice_events.jsonl")
        
        if log.exists():
            for line in log.read_text().splitlines():
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    if event["type"] == "track":
                        t = event["data"]
                        confidence = t.get("confidence", 0.0)
                        lat = t['location']['position']['latitudeDegrees']
                        lon = t['location']['position']['longitudeDegrees']
                        table.add_row(
                            t["entityId"][:8],
                            t["ontology"]["platform_type"][:6],
                            f"{confidence:.2f}",
                            f"{lat:.2f}",
                            f"{lon:.2f}"
                        )
                    elif event["type"] == "task":
                        priority = event['data'].get('priority', 'MEDIUM')
                        color = "red" if priority == "HIGH" else "yellow"
                        log_widget.write(f"[{color}]● {event['data']['description']}[/{color}]")
                except json.JSONDecodeError:
                    continue
    
    def action_refresh(self) -> None:
        self.load_tracks()
    
    def action_clear(self) -> None:
        """Clear the events log file and refresh."""
        log = Path("lattice_events.jsonl")
        if log.exists():
            log.unlink()
        self.load_tracks()

def main():
    app = SentryConsole()
    app.run()

if __name__ == "__main__":
    main()
