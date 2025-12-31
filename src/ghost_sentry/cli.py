"""Ghost Sentry CLI."""
import json
import typer
from pathlib import Path
from ghost_sentry.core.detector import ObjectDetector, Detection
from ghost_sentry.core.geo import mock_geo_location
from ghost_sentry.lattice.adapter import LatticeConnector
from ghost_sentry.core.sentry import process_detections

def detect(
    image_path: str = typer.Argument(..., help="Path to image"),
    mock: bool = typer.Option(False, help="Use mock detections for testing")
):
    """Detect objects in an image and publish to Lattice."""
    connector = LatticeConnector(mode="dev")
    
    if mock:
        # Load pre-made mock data
        root = Path(__file__).resolve().parent.parent.parent
        mock_file = root / "data/samples/mock_detections.json"
        
        if mock_file.exists():
            data = json.loads(mock_file.read_text())
            detections = [Detection(**d) for d in data]
            stats = process_detections(detections, connector)
            typer.echo(f"Successfully processed {stats['tracks']} tracks and {stats['tasks']} tasks (Mock)")
            return
        else:
            typer.echo(f"Error: Mock file not found at {mock_file}")
            raise typer.Exit(code=1)
    
    detector = ObjectDetector()
    detections = detector.detect(image_path)
    
    # Add mock geo if not available
    for d in detections:
        if d.geo_location is None:
            d.geo_location = mock_geo_location()
    
    stats = process_detections(detections, connector)
    typer.echo(f"Successfully processed {stats['tracks']} tracks and {stats['tasks']} tasks from {image_path}")

if __name__ == "__main__":
    typer.run(detect)
