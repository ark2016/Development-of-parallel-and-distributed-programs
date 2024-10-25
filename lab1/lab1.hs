import Control.Parallel
import Control.Parallel.Strategies
import System.Random
import Control.DeepSeq
import Data.Time.Clock

-- Генерация случайной матрицы размером rows x cols
generateMatrix :: Int -> Int -> IO [[Int]]
generateMatrix rows cols = do
    g <- newStdGen
    let randomList = take (rows * cols) $ randomRs (0, 9) g
    return $ splitEvery cols randomList

-- Вспомогательная функция для разделения списка на подсписки
splitEvery :: Int -> [a] -> [[a]]
splitEvery _ [] = []
splitEvery n xs = take n xs : splitEvery n (drop n xs)

-- Умножение двух матриц
multiplyMatrices :: [[Int]] -> [[Int]] -> [[Int]]
multiplyMatrices a b = let
    bt = transpose b
    in [ [ sum $ zipWith (*) ar bc | bc <- bt ] | ar <- a ]

-- Параллельное умножение двух матриц
multiplyMatricesParallel :: [[Int]] -> [[Int]] -> [[Int]]
multiplyMatricesParallel a b = let
    bt = transpose b
    in parMap rdeepseq (\ar -> [ sum $ zipWith (*) ar bc | bc <- bt ]) a

-- Транспонирование матрицы
transpose :: [[a]] -> [[a]]
transpose ([]:_) = []
transpose x = (map head x) : transpose (map tail x)

main :: IO ()
main = do
    let n = 1000
    a <- generateMatrix n n
    b <- generateMatrix n n

    start <- getCurrentTime
    let c = multiplyMatricesParallel a b
    c `deepseq` return ()  -- Гарантируем полное вычисление результата
    end <- getCurrentTime

    putStrLn $ "Time taken to multiply matrices: " ++ show (diffUTCTime end start)
    putStrLn $ "First element of result matrix: " ++ show (head $ head c)