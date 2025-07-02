class Process:
    """
    Represents a simplified process for memory management simulation.
    Only includes attributes necessary for memory allocation.
    """
    next_pid = 1  # Class-level variable to assign unique PIDs

    def __init__(self, size_required):
        """
        Initializes a new Process instance.

        Args:
            size_required (int): The amount of memory (in units) required by the process.
        """
        self.pid = Process.next_pid
        Process.next_pid += 1  # Increment for the next process

        self.size_required = size_required
        self.allocated_address = None  # Starting memory address if successfully allocated

    def __str__(self):
        """
        Returns a string representation of the Process for easy printing.
        """
        status = f"Allocated at {self.allocated_address} (Size: {self.size_required})" if self.allocated_address is not None else "Not Allocated"
        return f"P{self.pid}({self.size_required}u) -> {status}"

