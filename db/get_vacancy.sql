CREATE OR REPLACE FUNCTION get_vacancy(p_source VARCHAR, p_source_id VARCHAR)
RETURNS vacancies AS $$
DECLARE
    result vacancies;
BEGIN
    SELECT * INTO result FROM vacancies WHERE source = p_source AND source_id = p_source_id LIMIT 1;
    IF FOUND THEN
        RETURN result;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Check: --
-- SELECT get_vacancy('hh', '82365312');