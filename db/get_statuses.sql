CREATE OR REPLACE FUNCTION get_statuses(p_user INTEGER, p_vacancy INTEGER)
RETURNS TABLE (fav TEXT, res TEXT, rej TEXT, del TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT value FROM statuses WHERE user_id = p_user AND vacancy_id = p_vacancy AND status = 'FAV' ORDER BY created_at DESC LIMIT 1)::text AS fav,
        (SELECT value FROM statuses WHERE user_id = p_user AND vacancy_id = p_vacancy AND status = 'RES' ORDER BY created_at DESC LIMIT 1)::text AS res,
        (SELECT value FROM statuses WHERE user_id = p_user AND vacancy_id = p_vacancy AND status = 'REJ' ORDER BY created_at DESC LIMIT 1)::text AS rej,
        (SELECT value FROM statuses WHERE user_id = p_user AND vacancy_id = p_vacancy AND status = 'DEL' ORDER BY created_at DESC LIMIT 1)::text AS del;
END;
$$ LANGUAGE plpgsql;

-- check function --
-- SELECT * FROM get_statuses(0, 10);
-- SELECT * FROM get_statuses(0, 11);

