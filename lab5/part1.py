import threading
import time
import random


class EvolutionWorker(threading.Thread):
    def __init__(self, matrix, next_matrix, start_row, end_row, barrier_step, barrier_copy, num_steps, lock):
        super().__init__()
        self.matrix = matrix
        self.next_matrix = next_matrix
        self.start_row = start_row
        self.end_row = end_row
        self.barrier_step = barrier_step
        self.barrier_copy = barrier_copy
        self.num_steps = num_steps
        self.lock = lock
        self.rows = len(matrix)
        self.cols = len(matrix[0])

    def run(self):
        for _ in range(self.num_steps):
            # Compute next state for assigned rows
            for r in range(self.start_row, self.end_row):
                for c in range(self.cols):
                    alive_neighbors = self.count_neighbors(r, c)
                    cell = self.matrix[r][c]
                    if cell == 1:
                        # Alive cell rules
                        if alive_neighbors < 2 or alive_neighbors > 3:
                            self.next_matrix[r][c] = 0
                        else:
                            self.next_matrix[r][c] = 1
                    else:
                        # Dead cell rules
                        if alive_neighbors == 3:
                            self.next_matrix[r][c] = 1
                        else:
                            self.next_matrix[r][c] = 0

            # Wait until all threads finish computing next state
            self.barrier_step.wait()

            # Let one thread copy next_matrix to matrix
            self.barrier_copy.wait()

    def count_neighbors(self, r, c):
        neighbors = [
            (r - 1, c - 1), (r - 1, c), (r - 1, c + 1),
            (r, c - 1), (r, c + 1),
            (r + 1, c - 1), (r + 1, c), (r + 1, c + 1)
        ]
        count = 0
        for nr, nc in neighbors:
            nr = nr % self.rows
            nc = nc % self.cols
            count += self.matrix[nr][nc]
        return count


def run_evolution(rows, cols, steps, num_threads):
    # Initialize matrix with random 0/1
    matrix = [[random.randint(0, 1) for _ in range(cols)] for _ in range(rows)]
    next_matrix = [[0] * cols for _ in range(rows)]

    # If single-threaded, just run the simulation directly
    if num_threads == 1:
        start_time = time.time()
        for _ in range(steps):
            for r in range(rows):
                for c in range(cols):
                    # Count neighbors
                    neighbors = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            rr = (r + dr) % rows
                            cc = (c + dc) % cols
                            neighbors += matrix[rr][cc]
                    cell = matrix[r][c]
                    if cell == 1:
                        if neighbors < 2 or neighbors > 3:
                            next_matrix[r][c] = 0
                        else:
                            next_matrix[r][c] = 1
                    else:
                        if neighbors == 3:
                            next_matrix[r][c] = 1
                        else:
                            next_matrix[r][c] = 0
            # Copy next_matrix back
            matrix, next_matrix = next_matrix, matrix
        end_time = time.time()
        avg_time_per_step = (end_time - start_time) / steps
        return avg_time_per_step, None

    # Multithreaded execution
    # Divide rows among threads as evenly as possible
    rows_per_thread = rows // num_threads
    row_splits = []
    start = 0
    for i in range(num_threads):
        end = start + rows_per_thread
        if i == num_threads - 1:
            end = rows
        row_splits.append((start, end))
        start = end

    # Create two barriers:
    # barrier_step: Wait after computing next_matrix before copying
    # barrier_copy: Wait until the copy is done
    barrier_step = threading.Barrier(num_threads)
    barrier_copy = threading.Barrier(num_threads)
    lock = threading.Lock()

    workers = [EvolutionWorker(matrix, next_matrix, s, e, barrier_step, barrier_copy, steps, lock) for (s, e) in
               row_splits]

    start_time = time.time()
    for w in workers:
        w.start()



def run_evolution_with_threads(rows, cols, steps, num_threads):
    matrix = [[random.randint(0, 1) for _ in range(cols)] for _ in range(rows)]
    next_matrix = [[0] * cols for _ in range(rows)]

    # Divide rows among threads
    rows_per_thread = rows // num_threads
    row_splits = []
    start = 0
    for i in range(num_threads):
        end = start + rows_per_thread
        if i == num_threads - 1:
            end = rows
        row_splits.append((start, end))
        start = end

    barrier_step = threading.Barrier(num_threads)
    barrier_copy = threading.Barrier(num_threads)
    lock = threading.Lock()

    class EvolutionWorker(threading.Thread):
        def __init__(self, tid):
            super().__init__()
            self.tid = tid
            self.start_row, self.end_row = row_splits[tid]

        def run(self):
            for _ in range(steps):
                # Compute next state for assigned rows
                for r in range(self.start_row, self.end_row):
                    for c in range(cols):
                        alive_neighbors = self.count_neighbors(r, c)
                        cell = matrix[r][c]
                        if cell == 1:
                            if alive_neighbors < 2 or alive_neighbors > 3:
                                next_matrix[r][c] = 0
                            else:
                                next_matrix[r][c] = 1
                        else:
                            if alive_neighbors == 3:
                                next_matrix[r][c] = 1
                            else:
                                next_matrix[r][c] = 0

                # Wait until all threads finish computing next state
                barrier_step.wait()

                # One thread (tid=0) copies next_matrix to matrix
                if self.tid == 0:
                    for rr in range(rows):
                        for cc in range(cols):
                            matrix[rr][cc] = next_matrix[rr][cc]

                # Wait for the copying to finish
                barrier_copy.wait()

        def count_neighbors(self, r, c):
            total = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr = (r + dr) % rows
                    nc = (c + dc) % cols
                    total += matrix[nr][nc]
            return total

    workers = [EvolutionWorker(i) for i in range(num_threads)]
    start_time = time.time()
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    end_time = time.time()

    avg_time_per_step = (end_time - start_time) / steps
    return avg_time_per_step


# Example usage of the above functions:
if __name__ == "__main__":
    R, C = 200, 200
    steps = 50
    # Single-threaded
    single_thread_time, _ = run_evolution(R, C, steps, 1)
    print("Single-thread average time per step:", single_thread_time)

    # Multi-threaded
    for nt in [2, 4, 8]:
        mt_time = run_evolution_with_threads(R, C, steps, nt)
        print(f"{nt} threads average time per step:", mt_time)
