import logging

# Configure logging for the MemoryManager (optional, can be removed for minimal output)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - MEMORY - %(levelname)s - %(message)s')

class MemoryManager:
    """
    Manages the main memory space using First-Fit and Best-Fit allocation.
    Memory is represented as a list of block dictionaries.
    Each block: {'start': int, 'size': int, 'status': str, 'pid': int or None}
    """
    def __init__(self, total_memory_size):
        """
        Initializes the MemoryManager with a single large free block.

        Args:
            total_memory_size (int): The total size of memory in units.
        """
        if total_memory_size <= 0:
            raise ValueError("Total memory size must be positive.")
        
        self.total_memory_size = total_memory_size
        # Memory starts as one large free block
        self.memory = [{'start': 0, 'size': total_memory_size, 'status': 'free', 'pid': None}]
        self.current_strategy = None # Set by CLI: 'first_fit' or 'best_fit'

        logging.info(f"MemoryManager initialized with {total_memory_size} units.")
        self.display_memory_map() # Show initial state

    def _find_block_first_fit(self, size_required):
        """
        Finds the first free block that is large enough.
        """
        for i, block in enumerate(self.memory):
            if block['status'] == 'free' and block['size'] >= size_required:
                return i, block
        return None, None

    def _find_block_best_fit(self, size_required):
        """
        Finds the smallest free block that is large enough.
        """
        best_fit_index = None
        min_fragmentation = float('inf')

        for i, block in enumerate(self.memory):
            if block['status'] == 'free' and block['size'] >= size_required:
                fragmentation = block['size'] - size_required
                if fragmentation < min_fragmentation:
                    min_fragmentation = fragmentation
                    best_fit_index = i
        
        if best_fit_index is not None:
            return best_fit_index, self.memory[best_fit_index]
        return None, None

    def allocate_memory(self, process_id, size_required, strategy):
        """
        Allocates memory for a process using the specified strategy.

        Args:
            process_id (int): The ID of the process requesting memory.
            size_required (int): The amount of memory to allocate.
            strategy (str): The allocation strategy ('first_fit' or 'best_fit').

        Returns:
            int or None: The starting address of the allocated block if successful, else None.
        """
        if size_required <= 0:
            logging.warning(f"Allocation failed for PID {process_id}: Requested size must be positive.")
            return None

        find_block_func = {
            'first_fit': self._find_block_first_fit,
            'best_fit': self._find_block_best_fit
        }.get(strategy)

        if not find_block_func:
            logging.error(f"Invalid allocation strategy: {strategy}")
            return None

        block_index, block = find_block_func(size_required)

        if block:
            # If the block is an exact fit
            if block['size'] == size_required:
                block['status'] = 'occupied'
                block['pid'] = process_id
                logging.info(f"Allocated PID {process_id} with {size_required} units at {block['start']} (Exact Fit) using {strategy}.")
                return block['start']
            else:
                # Split the block: create an occupied block and a new free block for the remainder
                new_occupied_block = {
                    'start': block['start'],
                    'size': size_required,
                    'status': 'occupied',
                    'pid': process_id
                }
                new_free_block = {
                    'start': block['start'] + size_required,
                    'size': block['size'] - size_required,
                    'status': 'free',
                    'pid': None
                }
                # Replace the original free block with the new occupied block and the new free block
                self.memory[block_index:block_index+1] = [new_occupied_block, new_free_block]
                logging.info(f"Allocated PID {process_id} with {size_required} units at {new_occupied_block['start']} (Split) using {strategy}.")
                return new_occupied_block['start']
        else:
            logging.warning(f"Allocation failed for PID {process_id} (size {size_required}) using {strategy}: No suitable free block found.")
            return None

    def deallocate_memory(self, process_id):
        """
        Deallocates memory for a given process ID.
        Marks the block as free and attempts to coalesce adjacent free blocks.

        Args:
            process_id (int): The ID of the process whose memory is to be deallocated.

        Returns:
            bool: True if deallocation was successful, False otherwise.
        """
        found_block_index = None
        for i, block in enumerate(self.memory):
            if block['status'] == 'occupied' and block['pid'] == process_id:
                found_block_index = i
                break
        
        if found_block_index is None:
            logging.warning(f"Deallocation failed for PID {process_id}: Process not found or not allocated memory.")
            return False

        block_to_free = self.memory[found_block_index]
        block_to_free['status'] = 'free'
        block_to_free['pid'] = None
        logging.info(f"Deallocated memory for PID {process_id} at {block_to_free['start']} (size {block_to_free['size']}).")

        # Attempt to coalesce adjacent free blocks
        self._coalesce_free_blocks()
        return True

    def _coalesce_free_blocks(self):
        """
        Merges adjacent free blocks to reduce external fragmentation.
        Iterates through the memory list and combines contiguous free blocks.
        """
        new_memory = []
        i = 0
        while i < len(self.memory):
            current_block = self.memory[i]
            if current_block['status'] == 'free':
                # Try to merge with subsequent free blocks
                merged_block = current_block.copy()
                j = i + 1
                while j < len(self.memory) and self.memory[j]['status'] == 'free':
                    merged_block['size'] += self.memory[j]['size']
                    j += 1
                new_memory.append(merged_block)
                i = j # Move index past all merged blocks
            else:
                new_memory.append(current_block)
                i += 1
        self.memory = new_memory
        # Re-sort memory by start address to ensure logical order after coalescing
        self.memory.sort(key=lambda block: block['start'])
        logging.info("Coalescing completed. Memory defragmented.")

    def get_memory_utilization(self):
        """
        Calculates the current memory utilization.

        Returns:
            tuple: (occupied_memory_size, total_occupied_percentage, free_memory_size, total_free_percentage)
        """
        occupied_size = sum(block['size'] for block in self.memory if block['status'] == 'occupied')
        free_size = self.total_memory_size - occupied_size
        
        occupied_percentage = (occupied_size / self.total_memory_size) * 100 if self.total_memory_size > 0 else 0
        free_percentage = (free_size / self.total_memory_size) * 100 if self.total_memory_size > 0 else 0
        
        return occupied_size, occupied_percentage, free_size, free_percentage

    def get_free_block_info(self):
        """
        Provides information about free blocks.

        Returns:
            tuple: (num_free_blocks, largest_free_block, smallest_free_block)
        """
        free_blocks = [block['size'] for block in self.memory if block['status'] == 'free']
        num_free_blocks = len(free_blocks)
        largest_free_block = max(free_blocks) if free_blocks else 0
        smallest_free_block = min(free_blocks) if free_blocks else 0
        return num_free_blocks, largest_free_block, smallest_free_block

    def display_memory_map(self):
        """
        Prints a visual representation of the current memory state and utilization.
        """
        print("\n--- Memory Map ---")
        if not self.memory:
            print("Memory is empty.")
            return

        for block in self.memory:
            status_str = f"Occupied by P{block['pid']}" if block['status'] == 'occupied' else "FREE"
            print(f"  Addr: {block['start']}-{block['start'] + block['size'] - 1} | Size: {block['size']} | Status: {status_str}")
        
        occupied_size, occupied_percent, free_size, free_percent = self.get_memory_utilization()
        num_free, largest_free, smallest_free = self.get_free_block_info()

        print(f"\n--- Memory Utilization ---")
        print(f"  Total: {self.total_memory_size} units")
        print(f"  Occupied: {occupied_size} units ({occupied_percent:.2f}%)")
        print(f"  Free: {free_size} units ({free_percent:.2f}%)")
        print(f"  Free Blocks: {num_free} (Largest: {largest_free}, Smallest: {smallest_free})")
        print("---------------------------\n")

