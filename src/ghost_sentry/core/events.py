"""Core event bus for Ghost Sentry."""
from dataclasses import dataclass
from typing import Callable, List
import logging

@dataclass
class TrackEvent:
    entity_id: str
    data: dict

_listeners: List[Callable[[TrackEvent], None]] = []

def subscribe(callback: Callable[[TrackEvent], None]):
    """Subscribe a callback to track events."""
    _listeners.append(callback)
    logging.info(f"New subscriber added. Total: {len(_listeners)}")

def publish(event: TrackEvent):
    """Publish an event to all subscribers."""
    for listener in _listeners:
        try:
            listener(event)
        except Exception as e:
            logging.error(f"Error in event listener: {e}")
