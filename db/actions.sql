CREATE TABLE public.actions (
    id SERIAL NOT NULL,
    user_id INT NOT NULL,
    vacancy_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX actions_id ON public.actions USING btree (id);
CREATE INDEX actions_user ON public.actions USING btree (user_id);

