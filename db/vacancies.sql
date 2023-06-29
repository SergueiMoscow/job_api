CREATE TABLE public.vacancies (
    id BIGSERIAL NOT NULL,
    source VARCHAR NOT NULL,
    source_id VARCHAR(40) NOT NULL DEFAULT '',
    name VARCHAR(100) NOT NULL,
    area VARCHAR(50) DEFAULT NULL,
    salary_from INT DEFAULT 0,
    salary_to INT DEFAULT 0,
    salary_currency VARCHAR(3) NULL DEFAULT 'RUR',
    status VARCHAR(20) DEFAULT NULL,
    address_city VARCHAR(50) DEFAULT NULL,
    address_street VARCHAR(255) DEFAULT NULL,
    address_metro VARCHAR(30) DEFAULT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    url VARCHAR(255) DEFAULT NULL,
    url_api VARCHAR(255) DEFAULT NULL,
    employer_id VARCHAR(40) DEFAULT NULL,
    requirement TEXT DEFAULT NULL,
    responsibility TEXT DEFAULT NULL,
    experience VARCHAR(50) DEFAULT NULL,
    employment VARCHAR(50) DEFAULT NULL
);
CREATE INDEX vacancies_id ON public.vacancies USING btree (id);
CREATE INDEX vacancies_area ON public.vacancies USING btree (area);
CREATE INDEX vacancies_salary_from ON public.vacancies USING btree (salary_from);
