-- 判定。结论取值与参考实现 cmop_validation.chain 一致。
-- 终点仍有可走的父指针 = 在环上或挂在环上。
SELECT
    s.id,
    CASE
        WHEN e.has_parent                                              THEN 'cycle'
        WHEN e.dangling_self                                           THEN 'dangling_reference'
        WHEN e.ref_id IS NULL AND COALESCE(e.trans_type, '') <> '0'
             AND r.nxt = s.id                                          THEN 'missing_reference'
        WHEN e.ref_id IS NULL AND COALESCE(e.trans_type, '') <> '0'    THEN 'root_not_new'
        ELSE 'ok'
    END AS verdict,
    CASE WHEN e.has_parent OR e.dangling_self THEN NULL ELSE r.nxt END  AS root,
    CASE WHEN e.has_parent OR e.dangling_self THEN -1 ELSE r.dist END   AS depth
FROM {base} s
JOIN {prev} r ON s.id = r.id
JOIN {base} e ON r.nxt = e.id
