-- VA-11 / VC-10 第 0 步：解析每条报文的引用。
-- 输入 {src}(id, trans_type, ref_id)；id 唯一由驱动在执行前检查。
-- 语法限定在 DuckDB 与 Spark SQL 3.5 的交集内。
SELECT
    m.id,
    m.trans_type,
    m.ref_id,
    p.id IS NOT NULL                        AS has_parent,
    m.ref_id IS NOT NULL AND p.id IS NULL   AS dangling_self,
    CASE WHEN p.id IS NOT NULL THEN m.ref_id ELSE m.id END AS nxt,
    CASE WHEN p.id IS NOT NULL THEN 1 ELSE 0 END           AS dist
FROM {src} m
LEFT JOIN {src} p ON m.ref_id = p.id
