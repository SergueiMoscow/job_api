CREATE or REPLACE VIEW regions AS
SELECT DISTINCT 
	"area" AS area,
	COUNT("area") as cnt
FROM public.vacancies
GROUP BY area	
ORDER BY area;