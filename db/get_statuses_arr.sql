CREATE OR REPLACE FUNCTION get_statuses_arr(p_user INTEGER, p_vacancy INTEGER[])
RETURNS TABLE (vacancy_id INTEGER, fav TEXT, res TEXT, rej TEXT, del TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.vacancy_id,
        (SELECT value FROM statuses WHERE user_id = p_user AND vacancy_id = s.vacancy_id AND status = 'FAV' ORDER BY created_at DESC LIMIT 1)::text AS fav,
        (SELECT value FROM statuses WHERE user_id = p_user AND vacancy_id = s.vacancy_id AND status = 'RES' ORDER BY created_at DESC LIMIT 1)::text AS res,
        (SELECT value FROM statuses WHERE user_id = p_user AND vacancy_id = s.vacancy_id AND status = 'REJ' ORDER BY created_at DESC LIMIT 1)::text AS rej,
        (SELECT value FROM statuses WHERE user_id = p_user AND vacancy_id = s.vacancy_id AND status = 'DEL' ORDER BY created_at DESC LIMIT 1)::text AS del
    FROM
        statuses AS s
    WHERE
        s.vacancy_id IN (SELECT unnest(p_vacancy));
END;
$$ LANGUAGE plpgsql;

-- check function --
-- SELECT * FROM get_statuses(1, ARRAY[1, 2, 3]);
