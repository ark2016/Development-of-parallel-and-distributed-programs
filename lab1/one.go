package main

import (
	"math/rand"
)

func generateMatrix(rows, cols int) [][]int {
	matrix := make([][]int, rows)
	for i := 0; i < rows; i++ {
		matrix[i] = make([]int, cols)
		for j := 0; j < cols; j++ {
			matrix[i][j] = rand.Intn(10) // случайное число от 0 до 9
		}
	}
	return matrix
}

func multiplyMatrices(A, B [][]int) [][]int {
	rowsA, colsA := len(A), len(A[0])
	_, colsB := len(B), len(B[0])

	C := make([][]int, rowsA)
	for i := range C {
		C[i] = make([]int, colsB)
	}

	for i := 0; i < rowsA; i++ {
		for j := 0; j < colsB; j++ {
			for k := 0; k < colsA; k++ {
				C[i][j] += A[i][k] * B[k][j]
			}
		}
	}

	return C
}

//func main() {
//	a := 1000
//	rowsA, colsA := a, a
//	rowsB, colsB := a, a
//
//	rand.Seed(time.Now().UnixNano())
//	A := generateMatrix(rowsA, colsA)
//	B := generateMatrix(rowsB, colsB)
//
//	start := time.Now()
//	C := multiplyMatrices(A, B)
//	duration := time.Since(start)
//	fmt.Println(C[0][0])
//	fmt.Printf("Time taken to multiply matrices: %s\n", duration)
//}
