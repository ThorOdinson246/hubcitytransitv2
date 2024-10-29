class BusStateManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BusStateManager, cls).__new__(cls)
            cls._instance._bus_to_track = "blue1"  # default value
        return cls._instance
    
    @property
    def current_bus(self):
        return self._bus_to_track
    
    @current_bus.setter
    def current_bus(self, value):
        self._bus_to_track = value

# Create a singleton instance
bus_state = BusStateManager()