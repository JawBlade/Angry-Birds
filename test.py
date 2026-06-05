import time

# Start the timer
start_time = time.perf_counter()

# --- Put the code you want to time here ---
total = 0
for i in range(4):
    total += i
# ------------------------------------------

# End the timer
end_time = time.perf_counter()

# Calculate elapsed time in seconds
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.6f} seconds")