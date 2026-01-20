from PyQt6.QtCore import QObject, pyqtSignal
import math

class IntervalTracker(QObject):
    """
    Tracks price crossing interval boundaries with state change detection.
    
    - "돌파" (UP): price crosses above a boundary (e.g., 94999.9 -> 95000.1)
    - "깨어짐" (DOWN): price crosses below a boundary (e.g., 95000.1 -> 94999.9)
    
    Only emits signals when the state CHANGES. 
    If price oscillates around a boundary, only the first crossing in each direction triggers.
    """
    
    interval_crossed = pyqtSignal(float, str)  # (boundary_price, "UP" or "DOWN")

    def __init__(self, interval=50.0):
        super().__init__()
        self.interval = interval
        self.last_price = None
        
        # Track the last notified state for each boundary
        # Key: boundary (float), Value: last state ("ABOVE" or "BELOW")
        self.boundary_states = {}

    def set_interval(self, interval):
        self.interval = interval
        # Clear state when interval changes
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

        # Find the nearest boundaries around current price
        floor_boundary = math.floor(current_price / self.interval) * self.interval
        ceil_boundary = floor_boundary + self.interval
        
        # Check both boundaries
        for boundary in [floor_boundary, ceil_boundary]:
            current_state = self._get_state(current_price, boundary)
            
            # If price is exactly on boundary, no state change occurs
            if current_state == "EQUAL":
                continue
                
            # Get last known valid state for this boundary
            last_state = self.boundary_states.get(boundary)
            
            # If we haven't tracked this boundary yet, initialize it
            if last_state is None:
                self.boundary_states[boundary] = current_state
                continue
            
            # If state changed (and strictly different)
            if current_state != last_state:
                if current_state == "ABOVE" and last_state == "BELOW":
                    # Crossed UP
                    self.interval_crossed.emit(boundary, "UP")
                    self.boundary_states[boundary] = "ABOVE"
                elif current_state == "BELOW" and last_state == "ABOVE":
                    # Crossed DOWN
                    self.interval_crossed.emit(boundary, "DOWN")
                    self.boundary_states[boundary] = "BELOW"
        
        self.last_price = current_price
