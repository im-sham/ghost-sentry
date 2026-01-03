"""In-memory track state cache for analytics."""
from collections import defaultdict
from datetime import datetime
from typing import List, Tuple

# Store positions as: {entity_id: [(timestamp, (lat, lon)), ...]}
_track_positions: dict[str, List[Tuple[datetime, Tuple[float, float]]]] = defaultdict(list)

def update_position(entity_id: str, location: Tuple[float, float]):
    """Update the cached position for an entity."""
    _track_positions[entity_id].append((datetime.now(), location))
    # Keep only the last 20 positions for memory efficiency and analytics window
    _track_positions[entity_id] = _track_positions[entity_id][-20:]

def get_positions(entity_id: str) -> List[Tuple[datetime, Tuple[float, float]]]:
    """Retrieve the position history for an entity."""
    return _track_positions[entity_id]

def clear_cache():
    """Clear all cached positions."""
    _track_positions.clear()
