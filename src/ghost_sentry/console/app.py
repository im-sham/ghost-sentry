"""Ghost Sentry Operator Console."""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, RichLog, Static
from textual.containers import Horizontal, Vertical

from ghost_sentry.core import db

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
    
    CSS = CSS
    BINDINGS = [("q", "quit", "Quit"), ("r", "refresh", "Refresh")]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                Static("Detected Tracks", classes="title"),
                DataTable(id="tracks"),
                id="tracks-container"
            ),
            Vertical(
                Static("Cueing Tasks", classes="title"),
                RichLog(id="logs", markup=True),
                id="logs-container"
            ),
        )
        yield Footer()
    
    def on_mount(self) -> None:
        table = self.query_one("#tracks", DataTable)
        table.add_columns("ID", "Type", "Conf", "Lat", "Lon", "State")
        self.load_data()
    
    def load_data(self) -> None:
        table = self.query_one("#tracks", DataTable)
        table.clear()
        
        log_widget = self.query_one("#logs", RichLog)
        log_widget.clear()
        
        db.init_db()
        
        tracks = db.get_tracks()
        for t in tracks:
            try:
                confidence = t.get("confidence", 0.0)
                lat = t["location"]["position"]["latitudeDegrees"]
                lon = t["location"]["position"]["longitudeDegrees"]
                lifecycle = t.get("lifecycleState", "FIRM")
                table.add_row(
                    t["entityId"][:8],
                    t["ontology"]["platform_type"][:6],
                    f"{confidence:.2f}",
                    f"{lat:.2f}",
                    f"{lon:.2f}",
                    lifecycle[:4]
                )
            except (KeyError, TypeError):
                continue
        
        tasks = db.get_tasks()
        for task in tasks:
            try:
                priority = task.get("data", {}).get("priority", "MEDIUM") if task.get("data") else "MEDIUM"
                state = task.get("state", "pending")
                description = task.get("data", {}).get("description", "Unknown task") if task.get("data") else "Unknown task"
                
                if priority == "HIGH":
                    color = "red"
                elif state == "completed":
                    color = "green"
                else:
                    color = "yellow"
                
                state_icon = {"pending": "?", "assigned": ">", "in_progress": "~", "completed": "+", "cancelled": "x"}.get(state, "?")
                log_widget.write(f"[{color}][{state_icon}] {description}[/{color}]")
            except (KeyError, TypeError):
                continue
    
    def action_refresh(self) -> None:
        self.load_data()


def main():
    app = SentryConsole()
    app.run()


if __name__ == "__main__":
    main()
