import numpy as np
from numpy.linalg import norm
from cython.parallel import prange
from cython cimport boundscheck, wraparound, cdivision
from cython cimport parallel
import time  # Import the time module

cimport numpy as cnp

# Configuration parameters
cdef int MATRIX_SIZE = 2 ** 13
cdef double EPSILON = 1e-5

# Define data types for performance
ctypedef cnp.double_t DTYPE_t

@boundscheck(False)  # Disable bounds checking for better performance
@wraparound(False)   # Disable negative indexing for better performance
@cdivision(True)     # Allow C-style division
def initialize_matrix_and_vector():
    """Initialize matrix A and vector b."""
    cdef cnp.ndarray[DTYPE_t, ndim=2] A = np.full((MATRIX_SIZE, MATRIX_SIZE), 1, dtype=np.double)
    cdef cnp.ndarray[DTYPE_t, ndim=1] b = np.full(MATRIX_SIZE, MATRIX_SIZE + 1, dtype=np.double)
    cdef cnp.ndarray[DTYPE_t, ndim=1] x = np.zeros(MATRIX_SIZE, dtype=np.double)
    np.fill_diagonal(A, 2)
    return A, b, x

@boundscheck(False)
@wraparound(False)
def parallel_matrix_vector_multiply(cnp.ndarray[DTYPE_t, ndim=2] A, cnp.ndarray[DTYPE_t, ndim=1] v):
    """
    Perform matrix-vector multiplication in parallel using OpenMP.
    A: Input matrix
    v: Input vector
    """
    cdef int i, j
    cdef int n = A.shape[0]
    cdef cnp.ndarray[DTYPE_t, ndim=1] result = np.zeros(n, dtype=np.double)

    # OpenMP parallel loop
    with nogil, parallel.parallel():  # Release the GIL for parallel execution
        for i in prange(n):  # Use OpenMP to parallelize this loop
            for j in range(n):  # Inner loop remains serial
                result[i] += A[i, j] * v[j]

    return result

@boundscheck(False)
@wraparound(False)
def conjugate_gradient():
    """
    Conjugate Gradient Method to solve Ax = b.
    """
    cdef cnp.ndarray[DTYPE_t, ndim=2] A
    cdef cnp.ndarray[DTYPE_t, ndim=1] b, x, r, p, Ap
    cdef double alpha, beta, r_norm, b_norm
    cdef int i, max_iterations

    # Initialize variables
    A, b, x = initialize_matrix_and_vector()
    r = b - parallel_matrix_vector_multiply(A, x)
    p = r.copy()
    max_iterations = MATRIX_SIZE

    b_norm = norm(b)

    for i in range(max_iterations):
        Ap = parallel_matrix_vector_multiply(A, p)

        # Compute step size alpha
        alpha = np.dot(r, r) / np.dot(p, Ap)

        # Update x and residual r
        x += alpha * p
        old_r = r.copy()
        r -= alpha * Ap

        # Check for convergence
        r_norm = norm(r)
        if r_norm / b_norm < EPSILON:
            break

        # Compute beta and update p
        beta = np.dot(r, r) / np.dot(old_r, old_r)
        p = r + beta * p

    return x, i

def main():
    """Main function to run the conjugate gradient solver."""
    cdef double start_time, end_time
    cdef cnp.ndarray[DTYPE_t, ndim=1] solution
    cdef int iterations

    start_time = time.time()
    solution, iterations = conjugate_gradient()
    end_time = time.time()

    print(f"Matrix size: {MATRIX_SIZE}")
    print(f"Time taken: {end_time - start_time} seconds")
    print(f"Number of iterations: {iterations}")

