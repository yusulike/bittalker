from PyQt6.QtCore import QObject, pyqtSignal
import math

class IntervalTracker(QObject):
    """
    Tracks price crossing interval boundaries with state change detection.

    - "돌파" (UP): price crosses above a boundary (e.g., 94999.9 -> 95000.1)
    - "깨어짐" (DOWN): price crosses below a boundary (e.g., 95000.1 -> 94999.9)

    Every boundary between the previous and current price is checked, so a
    single tick that jumps multiple intervals still reports each crossing.
    Only emits signals when the state CHANGES.
    If price oscillates around a boundary, only the first crossing in each direction triggers.
    """

    interval_crossed = pyqtSignal(float, str)  # (boundary_price, "UP" or "DOWN")

    # Number of boundaries on each side of the current price whose state is kept
    KEEP_INTERVALS = 2

    def __init__(self, interval=50.0):
        super().__init__()
        self.interval = interval
        self.last_price = None

        # Track the last notified state for each boundary
        # Key: boundary (float), Value: last state ("ABOVE" or "BELOW")
        self.boundary_states = {}

    def set_interval(self, interval):
        self.interval = interval
        # Clear state when interval changes; states are re-inferred from
        # the next price so no crossing is falsely reported or missed
        self.boundary_states = {}

    def _get_state(self, price, boundary):
        """
        Determine if price is above or below the boundary.
        - ABOVE: price > boundary (strictly greater)
        - BELOW: price < boundary (strictly less)
        - EQUAL: price == boundary (no state change triggers)
        """
        if price > boundary:
            return "ABOVE"
        elif price < boundary:
            return "BELOW"
        else:
            return "EQUAL"

    def process_price(self, current_price):
        if self.last_price is None:
            self.last_price = current_price
            return

        # Check every boundary between the previous and current price so that
        # gaps larger than one interval don't skip crossings
        lower = min(self.last_price, current_price)
        upper = max(self.last_price, current_price)
        first_index = math.floor(lower / self.interval)
        last_index = math.floor(upper / self.interval)
        indices = range(first_index, last_index + 1)
        if current_price < self.last_price:
            indices = reversed(indices)  # emit in chronological crossing order

        for i in indices:
            self._check_boundary(current_price, i * self.interval)

        self.last_price = current_price
        self._prune_far_boundaries(current_price)

    def _check_boundary(self, current_price, boundary):
        current_state = self._get_state(current_price, boundary)

        # If price is exactly on boundary, no state change occurs
        if current_state == "EQUAL":
            return

        last_state = self.boundary_states.get(boundary)
        if last_state is None:
            # First time seeing this boundary: infer its previous side from
            # the previous price instead of silently adopting the current one
            last_state = self._get_state(self.last_price, boundary)
            if last_state == "EQUAL":
                return

        if current_state == "ABOVE" and last_state == "BELOW":
            # Crossed UP
            self.interval_crossed.emit(boundary, "UP")
        elif current_state == "BELOW" and last_state == "ABOVE":
            # Crossed DOWN
            self.interval_crossed.emit(boundary, "DOWN")

        self.boundary_states[boundary] = current_state

    def _prune_far_boundaries(self, price):
        """Drop tracked boundaries far from the current price to bound memory."""
        center = round(price / self.interval)
        low = (center - self.KEEP_INTERVALS) * self.interval
        high = (center + self.KEEP_INTERVALS) * self.interval
        for boundary in list(self.boundary_states):
            if boundary < low or boundary > high:
                del self.boundary_states[boundary]
