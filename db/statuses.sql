CREATE TABLE public.statuses (
    id SERIAL NOT NULL,
    user_id INT NOT NULL,
    vacancy_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    value VARCHAR(1) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX statuses_id ON public.statuses USING btree (id);
CREATE INDEX statuses_user ON public.statuses USING btree (user_id);
