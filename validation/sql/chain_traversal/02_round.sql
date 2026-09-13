-- 指针倍增的一轮：dist <- dist + dist[nxt]，nxt <- nxt[nxt]。
-- 驱动把上一轮结果物化为 {prev} 后重复执行 ceil(log2 n) + 1 次。
-- 必须逐轮物化：若写成嵌套 CTE，每轮引用上一轮两次，优化器内联后计划规模随轮数指数增长。
SELECT
    a.id,
    b.nxt,
    CAST(a.dist + b.dist AS BIGINT) AS dist
FROM {prev} a
JOIN {prev} b ON a.nxt = b.id
