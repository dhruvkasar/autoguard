from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time


@dataclass
class PersonState:
    last_zone: Optional[str] = None
    shelf_enter_time: Optional[float] = None
    visited_checkout: bool = False
    visited_shelf: bool = False
    transitions: List[str] = field(default_factory=list)  # sequence of zones


class BehaviorEngine:
    def __init__(self, loitering_seconds: int, shelf_exit_repeat_count: int, shelf_exit_time_window_seconds: int):
        self.loitering_seconds = loitering_seconds
        self.repeat_count = shelf_exit_repeat_count
        self.time_window = shelf_exit_time_window_seconds
        self.persons: Dict[int, PersonState] = {}
        self.transition_times: Dict[int, List[float]] = {}

    def update(self, person_id: int, zone: Optional[str], now: Optional[float] = None, crossed_checkout: bool = False) -> List[str]:
        """Update state for a person and return triggered rule names."""
        if now is None:
            now = time.time()
        state = self.persons.setdefault(person_id, PersonState())
        triggers: List[str] = []

        if crossed_checkout:
            state.visited_checkout = True

        if zone is None:
            # Left zones; if loitering timer running, stop it
            if state.last_zone == "shelf" and state.shelf_enter_time:
                # Reset timer when leaving shelf
                state.shelf_enter_time = None
            state.last_zone = None
            return triggers

        # Zone entry/transition handling
        if zone != state.last_zone:
            # record transition
            state.transitions.append(zone)
            self.transition_times.setdefault(person_id, []).append(now)

            if zone == "shelf":
                state.visited_shelf = True
                state.shelf_enter_time = now
            elif zone == "checkout":
                state.visited_checkout = True
                # leaving shelf: stop loitering timer
                state.shelf_enter_time = None
            elif zone == "exit":
                # check rules dependent on exit
                if state.visited_shelf and not state.visited_checkout:
                    triggers.append("Exit Without Checkout")

            # Check repeated shelf-exit movement within window
            transitions = state.transitions
            times = self.transition_times.get(person_id, [])
            # look back within time window
            recent = [(z, t) for z, t in zip(transitions, times) if now - t <= self.time_window]
            # count pattern occurrences: we consider simply the count of 'shelf' and 'exit' transitions
            shelf_count = sum(1 for z, _ in recent if z == "shelf")
            exit_count = sum(1 for z, _ in recent if z == "exit")
            if shelf_count >= self.repeat_count and exit_count >= self.repeat_count:
                triggers.append("Repeated Shelf–Exit Movement")

            state.last_zone = zone

        # Loitering rule: staying inside shelf beyond threshold
        if zone == "shelf" and state.shelf_enter_time:
            if (now - state.shelf_enter_time) >= self.loitering_seconds:
                triggers.append("Loitering in Shelf Zone")
                # prevent continuous firing; reset timer
                state.shelf_enter_time = now  # continue monitoring but avoid spam
        return triggers
