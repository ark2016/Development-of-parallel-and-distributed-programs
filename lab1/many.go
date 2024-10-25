package main

import (
	"fmt"
	"math/rand"
	"runtime"
	"sync"
	"time"
)

func generateMatrix1(rows, cols int) [][]int {
	matrix := make([][]int, rows)
	for i := 0; i < rows; i++ {
		matrix[i] = make([]int, cols)
		for j := 0; j < cols; j++ {
			matrix[i][j] = rand.Intn(10)
		}
	}
	return matrix
}

func multiplyMatrices1(A, B [][]int) [][]int {
	rowsA, colsA := len(A), len(A[0])
	_, colsB := len(B), len(B[0])

	C := make([][]int, rowsA)
	for i := range C {
		C[i] = make([]int, colsB)
	}

	var wg sync.WaitGroup

	for i := 0; i < rowsA; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			for j := 0; j < colsB; j++ {
				for k := 0; k < colsA; k++ {
					C[i][j] += A[i][k] * B[k][j]
				}
			}
		}(i)
	}
	fmt.Printf("Number of goroutines %d\n", runtime.NumGoroutine())

	wg.Wait()

	return C
}

func main() {
	a := 1000
	rowsA, colsA := a, a
	rowsB, colsB := a, a

	rand.Seed(time.Now().UnixNano())
	A := generateMatrix1(rowsA, colsA)
	B := generateMatrix1(rowsB, colsB)

	start := time.Now()
	C := multiplyMatrices1(A, B)
	duration := time.Since(start)

	fmt.Println(C[0][0])
	fmt.Printf("Time taken to multiply matrices: %s\n", duration)
}
