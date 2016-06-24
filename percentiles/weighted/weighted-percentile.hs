import System.Environment (getArgs)
import Text.Printf (printf)
import Text.ParserCombinators.Parsec
import Data.CSV

--ordinal_rank :: Double -> Int -> Int
ordinal_rank p n = ceiling (p * (fI n))

-- Get the rank at which the partial sum of ws surpasses 'target'
_wr [] _ _     = undefined
_wr (w:[]) _ _ = 1
_wr (w:ws) target cur
  | target < cur + w = 1
  | otherwise         = 1 + (_wr ws target (cur + w))

-- Get the rank before which the partial sum of ws surpasses the given percentile
weighted_rank :: Double -> [Double] -> Int
weighted_rank p ws
  | length ws == 0 = undefined
  | length ws == 1 = 1
  | otherwise      = (_wr ws (p * (sum ws)) 0.0) - 1

s_n :: Int -> [Double] -> Double
s_n n ws = sum $ take n ws

-- 1-indexed
nth _ [] = undefined
nth 0 (x:xs) = x
nth n xs = xs !! (n-1)

p_n n ws = (1.0 / (s_n (length ws) ws)) * (s_n n ws - (nth n ws / 2.0))

-- Value of (weighted) percentile p:
weighted_percentile :: Double -> [Double] -> [Double] -> Double
weighted_percentile p vs ws =
  let len = length vs
      k   = weighted_rank p ws
      vk  = nth k vs
      vk1 = nth (k + 1) vs
-- No weights (i.e. all weights of 1):
--      pk  = fI k / len
--      pk1 = fI (k + 1) / len
      pk  = p_n k ws
      pk1 = p_n (k + 1) ws
  in vk + (vk1 - vk) * (p - pk) / (pk1 - pk)

fI = fromIntegral

values :: [Double]
values = map fI [1,2,3,4,5,6,7,8,9,10] 

weights = take 10 $ repeat 1

uSEC_PER_MS = 1.0

-- True iff the given sample falls in the interval
interval_contains :: (Int,Int) -> [Int] -> Bool
interval_contains (start,end) (time:value:rest) =
      time >= start && time < end
  ||  fI time + fI value / uSEC_PER_MS > fI start && fI time + fI value / uSEC_PER_MS <= fI end

-- Get samples falling in given interval
interval_samples :: Int -> Int -> [[Int]] -> [[Int]]
interval_samples start end = filter (interval_contains (start,end))

-- Round to multiple of given divisor:
round_down :: Int -> Int -> Int
round_down divisor n = (round (fI n / fI divisor)) * divisor
round_up   divisor n = (round_down divisor n) + divisor

-- Compute the necessary intervals:
get_intervals :: Int -> [[Int]] -> [(Int,Int)]
get_intervals width ss =
  let ss' = map head ss
      mn  = round_down 1000 $ minimum ss'
      mx  = round_up   1000 $ maximum ss'
      n_interval = [0 .. (truncate $ fI (mx - mn) / fI width) - 1]
  in [(mn + a*width, mn + (a+1)*width) | a <- n_interval ]

sample_weight :: Int -> Int -> [Int] -> Double
sample_weight start end (time:value:_)
  | end < time || fI start > fI time + fI value / uSEC_PER_MS = 0
  | otherwise = let
      sbound = fI $ max start time
      ebound = min (fI end) (fI time + fI value / uSEC_PER_MS)
    in (ebound - sbound) / fI (end - start)

show' :: Double -> String
show' x = printf "%.3f, " x

weighted_average vs ws = sum (map (\(w,v) -> w*v) (zip ws vs)) / sum ws

show_stats _ _ [] = return ()
show_stats _ _ (x:[]) = return ()
show_stats start end ss = do
  let ws = map (sample_weight start end) ss
  let vs = map (fI . (!!1)) ss
  let ps = map (\p -> weighted_percentile p vs ws) [0.50, 0.90, 0.95, 0.99]
  putStr $ show' (fI end) ++ show (length ss) ++ ", "
  putStr $ show' $ minimum vs
  putStr $ show' $ weighted_average vs ws
  mapM (putStr . show') ps
  putStrLn $ show $ maximum vs
  --putStrLn $ show start ++ ", " ++ show end ++ ", " ++ show ss

main = do
  args <- getArgs
  Right result <- parseFromFile csvFile $ head args
  let r = map (map read) result :: [[Int]]
  let intervals = get_intervals 1000 r :: [(Int,Int)]
  putStrLn "end-time, samples, min, avg, median, 90%, 95%, 99%, max"
  mapM (\(s,e) -> 
    show_stats s e $ interval_samples s e r) intervals
  return ()
--  let r2 = map interval_samples 
--  filter (interval_contains 0 1000) r



