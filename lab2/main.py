import sys
from mpi4py import MPI
import numpy as np
from numpy.linalg import norm

#mpiexec -n 4  python main.py > results.txt

np.random.seed(42)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Конфигурационные параметры
MATRIX_SIZE = 2 ** 13
MATRIX_SPLIT = int(sys.argv[1]) if len(sys.argv) > 1 else size  # По умолчанию использует количество процессов
EPSILON = 1e-5


def initialize_matrix_and_vector():
    """Инициализация матрицы A и вектора b."""
    A = np.full((MATRIX_SIZE, MATRIX_SIZE), 1, dtype=np.double)
    np.fill_diagonal(A, 2)
    b = np.full(MATRIX_SIZE, MATRIX_SIZE + 1, dtype=np.double)
    x = np.zeros(MATRIX_SIZE, dtype=np.double)
    return A, b, x


def parallel_matrix_vector_multiply(A, v):
    """Параллельное умножение матрицы на вектор."""
    local_size = MATRIX_SIZE // MATRIX_SPLIT
    local_A = np.empty((local_size, MATRIX_SIZE), dtype=np.double)
    v = comm.bcast(v, root=0)

    comm.Scatter(A, local_A, root=0)
    local_result = np.dot(local_A, v)

    result = np.empty(MATRIX_SIZE, dtype=np.double) if rank == 0 else None
    comm.Gather(local_result, result, root=0)

    return comm.bcast(result, root=0)


def conjugate_gradient():
    """Метод сопряженных градиентов."""
    A, b, x = initialize_matrix_and_vector()

    A = comm.bcast(A, root=0)
    b = comm.bcast(b, root=0)

    r = b - parallel_matrix_vector_multiply(A, x)
    p = r.copy()

    for i in range(MATRIX_SIZE):  # Максимальное количество итераций
        Ap = parallel_matrix_vector_multiply(A, p)

        alpha = np.dot(r, r) / np.dot(p, Ap)
        x = x + alpha * p
        old_r = r.copy()
        r = r - alpha * Ap

        if norm(r) / norm(b) < EPSILON:
            break

        beta = np.dot(r, r) / np.dot(old_r, old_r)
        p = r + beta * p

    return x, i


if __name__ == "__main__":
    start_time = MPI.Wtime()
    solution, iterations = conjugate_gradient()
    end_time = MPI.Wtime()

    if rank == 0:
        print(f"Number of processes: {size}, Matrix split factor: {MATRIX_SPLIT}")
        print(f"Time taken: {end_time - start_time} seconds")
        print(f"Number of iterations: {iterations}")
