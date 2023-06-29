CREATE TABLE public.queries (
    id SERIAL NOT NULL,
    user_id INT NOT NULL DEFAULT 0,
    text VARCHAR(50) NOT NULL,
    date_from DATE NOT NULL,
    date_to DATE NOT NULL,
    source VARCHAR(10) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    error VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX queries_id ON public.queries USING btree (id);
CREATE INDEX queries_user ON public.queries USING btree (user_id);
