import logging
from process import Process
from memory_manager import MemoryManager

# Configure logging for the main CLI (optional, can be removed for minimal output)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CLI - %(levelname)s - %(message)s')

def run_cli():
    """
    Runs the command-line interface for the Memory Management simulation.
    """
    print("--- Simple OS Memory Management Simulator ---")
    print("Welcome! Let's configure the memory.")

    total_memory = None
    while total_memory is None:
        try:
            total_memory = int(input("Enter total memory size (e.g., 1000 units): ").strip())
            if total_memory <= 0:
                print("Memory size must be a positive integer. Please try again.")
                total_memory = None
        except ValueError:
            print("Invalid input. Please enter an integer for memory size.")
    
    manager = MemoryManager(total_memory)
    # Dictionary to keep track of active processes: {pid: Process_object}
    # This is crucial to know which PID corresponds to which allocated memory.
    processes = {} 

    # Set initial strategy
    current_strategy = None
    while current_strategy not in ['first_fit', 'best_fit']:
        print("\nSelect initial allocation strategy:")
        print("  1. First-Fit")
        print("  2. Best-Fit")
        choice = input("Enter choice (1 or 2): ").strip()
        if choice == '1':
            current_strategy = 'first_fit'
        elif choice == '2':
            current_strategy = 'best_fit'
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    manager.current_strategy = current_strategy # Update manager's internal strategy
    print(f"\nMemory allocation strategy set to: {current_strategy.replace('_', '-').title()}")
    logging.info(f"Initial strategy set to: {current_strategy}")

    print("\n--- Commands ---")
    print("  allocate <size>       - Allocate memory for a new process (e.g., allocate 100)")
    print("  deallocate <pid>      - Deallocate memory for a process (e.g., deallocate 1)")
    print("  strategy <name>       - Change allocation strategy (first_fit, best_fit)")
    print("  map                   - Display current memory map and utilization")
    print("  quit                  - Exit the simulator")
    print("------------------\n")

    while True:
        try:
            command_line = input(f"[{current_strategy.replace('_', '-')}] > ").strip().lower()
            parts = command_line.split()
            command = parts[0] if parts else ''

            if command == 'quit':
                print("Exiting simulator. Goodbye!")
                break
            elif command == 'allocate':
                if len(parts) == 2:
                    try:
                        size = int(parts[1])
                        new_process = Process(size) # Create a new Process object
                        logging.info(f"Attempting to allocate P{new_process.pid} with size {size} using {current_strategy}.")
                        
                        allocated_address = manager.allocate_memory(new_process.pid, size, current_strategy)
                        
                        if allocated_address is not None:
                            new_process.allocated_address = allocated_address
                            processes[new_process.pid] = new_process # Store the process object
                            print(f"Allocated memory for {new_process}.")
                        else:
                            print(f"Failed to allocate memory for P{new_process.pid} (size {size}).")
                        manager.display_memory_map()
                    except ValueError:
                        print("Invalid size. Please enter an integer.")
                else:
                    print("Usage: allocate <size>")
            elif command == 'deallocate':
                if len(parts) == 2:
                    try:
                        pid_to_deallocate = int(parts[1])
                        if pid_to_deallocate in processes:
                            logging.info(f"Attempting to deallocate P{pid_to_deallocate}.")
                            success = manager.deallocate_memory(pid_to_deallocate)
                            if success:
                                del processes[pid_to_deallocate] # Remove from active processes
                                print(f"Deallocated memory for P{pid_to_deallocate}.")
                            else:
                                print(f"Failed to deallocate memory for P{pid_to_deallocate}.")
                            manager.display_memory_map()
                        else:
                            print(f"P{pid_to_deallocate} not found or not currently allocated memory.")
                    except ValueError:
                        print("Invalid PID. Please enter an integer.")
                else:
                    print("Usage: deallocate <pid>")
            elif command == 'strategy':
                if len(parts) == 2:
                    new_strategy = parts[1].lower()
                    if new_strategy in ['first_fit', 'best_fit']:
                        current_strategy = new_strategy
                        manager.current_strategy = current_strategy # Update manager's internal strategy
                        print(f"Memory allocation strategy changed to: {current_strategy.replace('_', '-').title()}")
                        logging.info(f"Strategy changed to: {current_strategy}")
                    else:
                        print("Invalid strategy name. Choose from: first_fit, best_fit.")
                else:
                    print("Usage: strategy <name> (e.g., strategy best_fit)")
            elif command == 'map':
                manager.display_memory_map()
            else:
                print("Unknown command. Type 'help' for commands or refer to the list above.")

        except Exception as e:
            logging.error(f"An unexpected error occurred in CLI: {e}")
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_cli()

