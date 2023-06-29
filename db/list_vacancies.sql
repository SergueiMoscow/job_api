!!! NOT TERMINATED !!!
!!! DON'T EXECUTE IT!!!

CREATE OR REPLACE
FUNCTION public.list_vacancies(
    p_keyword VARCHAR DEFAULT NULL,
    p_status VARCHAR DEFAULT NULL,
    p_region VARCHAR DEFAULT NULL
)
RETURNS SETOF vacancies LANGUAGE plpgsql AS $function$
DECLARE
	s_keyword VARCHAR := CONCAT('%', p_keyword, '%');
BEGIN
    RETURN QUERY
    SELECT * FROM vacancies
    LEFT JOIN statuses ON vacancies.id = statuses.vacancy_id
    WHERE
    	(name LIKE s_keyword OR requirement LIKE s_keyword OR responsibility LIKE s_keyword)
    	AND
    	area =
        CASE WHEN p_region IS NULL THEN '' ELSE p_region END
    ORDER BY published_at DESC;
    END;
$function$;

select * from list_vacancies('python', NULL, 'Москва'); -- for voucher 322
select * from list_vacancies(p_region => 'г. Москва'); -- for transaction id 322
