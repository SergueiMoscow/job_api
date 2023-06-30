from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, func, DateTime, Boolean, Text, Index, Date, TIMESTAMP, \
    text
import os
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
str_engine = f"postgresql://{os.getenv('pgsql_user')}:{os.getenv('pgsql_password')}@" \
             f"{os.getenv('pgsql_host')}/{os.getenv('pgsql_db')}"
engine = create_engine(str_engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    password = Column(String)
    email = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), index=True)
    deleted_at = Column(DateTime, index=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, index=True)


class Vacancy(Base):
    __tablename__ = 'vacancies'

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    source_id = Column(String(40), nullable=False, default='')
    name = Column(String(100), nullable=False)
    area = Column(String(50))
    salary_from = Column(Integer, default=0)
    salary_to = Column(Integer, default=0)
    salary_currency = Column(String(3), default='RUR')
    status = Column(String(20))
    address_city = Column(String(50))
    address_street = Column(String(255))
    address_metro = Column(String(30))
    published_at = Column(DateTime(timezone=True))
    url = Column(String(255))
    url_api = Column(String(255))
    employer_id = Column(String(40))
    requirement = Column(Text)
    responsibility = Column(Text)
    experience = Column(String(50))
    employment = Column(String(50))

    __table_args__ = (
        Index('ix_vacancy_soucre_id', 'source', 'source_id'),
        Index('ix_vacancy_area', 'area'),
        Index('ix_salary_from', 'salary_from'),
        {'schema': 'public'}
    )

    Index('ix_vacancy_soucre_id', 'source', 'source_id')
    Index('ix_vacancy_area', 'area')
    Index('ix_salary_from', 'salary_from')


class Query(Base):
    __tablename__ = 'queries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=0)
    text = Column(String(50), nullable=False)
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    source = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    error = Column(String(255), nullable=False, default='')
    created_at = Column(DateTime, server_default=func.now(), index=True)

    __table_args__ = (
        Index('ix_user_id', 'user_id'),
        {'schema': 'public'}
    )


def check_functions():
    functions = [
        'get_statuses',
        'get_statuses_arr',
        'get_vacancy',
    ]
    for func_name in functions:
        _session = sessionmaker(bind=engine)
        session = _session()
        query = f"""
                SELECT routine_name
                FROM information_schema.routines
                WHERE routine_name = '{func_name}'
                """
        result = session.execute(text(query)).fetchone()
        if result is None:
            with open(f'../db/{func_name}.sql', 'r') as f:
                sql_create_function = f.read()
                created = session.execute(text(sql_create_function))
                session.commit()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    check_functions()
