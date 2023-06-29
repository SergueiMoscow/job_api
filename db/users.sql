CREATE TABLE public.users (
    id SERIAL NOT NULL,
    login VARCHAR(20) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(50) NOT NULL,
);

CREATE INDEX users_id ON public.users USING btree (id);
CREATE INDEX users_login ON public.users USING btree (login);
CREATE INDEX users_email ON public.users USING btree (email);
