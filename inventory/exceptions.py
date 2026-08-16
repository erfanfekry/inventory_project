class InsufficientInventoryError(Exception):
    """Raised when there is not enough inventory for a decrease operation."""

    def __init__(self, message="Insufficient inventory."):
        self.message = message
        super().__init__(self.message)