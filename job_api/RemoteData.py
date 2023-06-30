import math

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import requests
from datetime import timedelta, date, datetime
from job_api.models import engine, Vacancy, Query
from job_api.logger import debug, info, error

HH_URL = "https://api.hh.ru/vacancies"
TRUD_VSEM_URL = "http://opendata.trudvsem.ru/api/v1/vacancies"


class RemoteData:
    fields = [
        'source',
        'source_id',
        'name',
        'area',
        'salary_from',
        'salary_to',
        'salary_currency',
        'status',
        'address_city',
        'address_street',
        'address_metro',
        'published_at',
        'url',
        'url_api',
        'employer_id',
        'requirement',
        'responsibility',
        'experience',
        'employment'
    ]
    session = None
    user_id = 0
    updated_records = 0
    inserted_records = 0

    @classmethod
    def __set_db(cls):
        if cls.session is None:
            _session = sessionmaker(bind=engine)
            cls.session = _session()

    @classmethod
    def get_hh_list(cls, text: str, area: str, period: int = 5) -> int:
        """
        Получаем список вакансий по запросу из hh.ru

        Args:
            text: текст, который должен содержаться в вакансии
            area: район
            period: период в днях

        Returns:
            количество подгруженных и обработанных вакансий
        """
        # https://api.hh.ru/vacancies?per_page=10&page=0&period=2&text=python&experience=noExperience
        url = f'{HH_URL}'
        params = {
            "per_page": 50,
            "page": 0,
            "period": period,
            "text": text,
            "experience": None,
            "employment": None,
            "schedule": None,
        }
        date_from = date.today() - timedelta(days=period)
        date_to = date.today() - timedelta(days=1)
        source = 'hh.ru'
        num_loaded = 0

        result = requests.get(HH_URL, params)
        if not result.ok:
            cls.__log_query(
                text=text,
                date_from=date_from,
                date_to=date_to,
                source=source,
                quantity=0,
                error="Error get_hh_list can't load data"
            )
            error("Error get_hh_list can't load data")
            return -1
        vacancies = result.json()['items']
        num_loaded += cls.__vacancies_hh(vacancies)
        pages = result.json()['pages']
        for page in range(1, pages):
            params['page'] = page
            result = requests.get(HH_URL, params)
            if result.ok:
                vacancies = result.json()['items']
                num_loaded += cls.__vacancies_hh(vacancies)
        cls.__log_query(
            text=text,
            date_from=date_from,
            date_to=date_to,
            source=source,
            quantity=num_loaded,
            error=""
        )
        return num_loaded

    @staticmethod
    def get_hh_one(vacancy_id: int) -> bool:
        pass

    @classmethod
    def __vacancies_hh(cls, vacancies: dict) -> int:
        """
        Парсит JSON из hh.ru, создавая для каждого объект вакансии

        Args:
            vacancies: - dictionary (JSON из hh.ru)

        Returns:
            количество обработанных вакансий:
        """
        cls.__set_db()
        num_processed = 0
        for vacancy in vacancies:
            if vacancy['salary'] is not None:
                salary_from = vacancy['salary']['from']
                salary_to = vacancy['salary']['to']
                salary_currency = vacancy['salary']['currency']
            else:
                salary_from, salary_to, salary_currency = None, None, None
            if vacancy['address'] is not None:
                address_city = vacancy['address']['city']
                address_raw = vacancy['address']['raw']
                if vacancy['address']['metro'] is not None:
                    address_metro = vacancy['address']['metro']['station_name']
                else:
                    address_metro = None
            else:
                address_city, address_raw, address_metro = None, None, None
            if 'employer' in vacancy:
                if 'id' in vacancy['employer']:
                    employer_id = vacancy['employer']['id']
                else:
                    employer_id = None
            else:
                employer_id = None
            new_vacancy = Vacancy(
                source='hh.ru',
                source_id=vacancy['id'],
                name=vacancy['name'],
                area=vacancy['area']['name'],
                salary_from=salary_from,
                salary_to=salary_to,
                salary_currency=salary_currency,
                status=vacancy['type']['name'],
                address_city=address_city,
                address_street=address_raw,
                address_metro=address_metro,
                published_at=vacancy['published_at'],
                url=vacancy['alternate_url'],
                url_api=vacancy['url'],
                employer_id=employer_id,
                requirement=vacancy['snippet']['requirement'],
                responsibility=vacancy['snippet']['responsibility'],
                experience=vacancy['experience']['name'],
                employment=vacancy['employment']['name']
            )
            cls.__save(new_vacancy)
            num_processed += 1
        return num_processed

    @classmethod
    def __save(cls, new_vacancy: Vacancy) -> None:
        """
        Сохраняет вакансию в базу данных, после проверки на существования по source и source_id

        Args:
            new_vacancy: Vacancy object

        Returns:
            None
        """

        function = text("SELECT * FROM get_vacancy(:source, :source_id)")
        rows = cls.session.execute(function, {'source': new_vacancy.source, 'source_id': new_vacancy.source_id})
        result = rows.fetchone()
        if result[0] is None:
            debug(f'Vacancy not found: {new_vacancy.source} - {new_vacancy.source_id}')
            cls.session.add(new_vacancy)
            cls.inserted_records += 1
        else:
            # cls.session.merge(new_vacancy)
            # merge не работает должным образом, вставляет данные вместо update.
            # Костыль?
            new_vacancy.id = result[0]
            cls.session.merge(new_vacancy)
            cls.updated_records += 1
        cls.session.commit()

    @classmethod
    def get_trud_vsem_list(cls, text: str, area: str, period: int = 5):
        """
        Получаем список вакансий по запросу из trudvsem.ru

        Args:
            text: текст, который должен содержаться в вакансии
            area: район
            period: период в днях

        Returns:
            количество подгруженных и обработанных вакансий
        """
        date_from = date.today() - timedelta(days=period)
        date_to = date.today() - timedelta(days=1)
        source = 'trudvsem'
        num_loaded = 0
        modified_from_date = date.today() - timedelta(days=period)
        modified_from = f'{modified_from_date}T00:00:00Z'
        limit = 50
        params = {
            'text': text,
            'offset': 0,
            'limit': limit,
            'modifiedFrom': modified_from
        }
        result = requests.get(TRUD_VSEM_URL, params)
        if not result.ok:
            return "Error get_trud_vsem_list can't load data"
        vacancies = result.json()['results']['vacancies']
        num_loaded += cls.__vacancies_trud_vsem(vacancies)
        total = result.json()['meta']['total']
        pages = math.ceil(total / limit)
        for page in range(1, pages):
            # Странно, но offset считают так
            params['offset'] = page  # (page - 1) * limit + 1
            result = requests.get(TRUD_VSEM_URL, params)
            if 'results' in result.json():
                vacancies = result.json()['results']['vacancies']
                num_loaded += cls.__vacancies_trud_vsem(vacancies)
            else:
                info(f"No results in {result.json()}")
        cls.__log_query(
            text=text,
            date_from=date_from,
            date_to=date_to,
            source=source,
            quantity=num_loaded,
            error=""
        )
        return num_loaded



    @classmethod
    def __vacancies_trud_vsem(cls, vacancies: list) -> int:
        """
        Парсит JSON из trudvsem.ru, создавая для каждого объекта JSON объект Vacancy

        Args:
            vacancies: - list (JSON из trudvsem.ru)

        Returns:
            количество обработанных вакансий
        """
        cls.__set_db()
        num_processed = 0
        for item in vacancies:
            vacancy = item['vacancy']
            if isinstance(vacancy['addresses'], dict):
                address_raw = vacancy['addresses']['address'][0]['location'][:255]
            else:
                address_raw = None
            if 'name' in vacancy['region']:
                region = vacancy['region']['name']
            else:
                if 'region_code' in vacancy['region']:
                    region = vacancy['region']['region_code']
                else:
                    region = ''
            if 'qualification' in vacancy['requirement']:
                qualification = vacancy['requirement']['qualification']
            else:
                qualification = ''
            new_vacancy = Vacancy(
                source='trudvsem',
                source_id=vacancy['id'],
                name=vacancy['job-name'],
                area=region,
                salary_from=vacancy['salary_min'],
                salary_to=vacancy['salary_max'],
                salary_currency=vacancy['currency'][:3],
                status='?',
                address_city=None,
                address_street=address_raw,
                address_metro=None,
                published_at=vacancy['creation-date'],
                url=vacancy['vac_url'],
                url_api=f"{TRUD_VSEM_URL}/vacancy/{vacancy['company']['companycode']}/{vacancy['id']}",
                employer_id=vacancy['company']['companycode'],
                requirement=f"{vacancy['requirement']['education']}/{qualification}",
                responsibility=vacancy['duty'],
                experience=vacancy['requirement']['experience'],
                employment=vacancy['employment']
            )
            cls.__save(new_vacancy)
            num_processed += 1
        return num_processed

    @classmethod
    def __log_query(
            cls,
            text: str,
            date_from: date,
            date_to: date,
            source: str,
            quantity: int,
            error: str = '',
    ) -> None:
        """
        Регистрирует результаты раоты в таблице queries

        Args:
            text: - ключевое слово поиска
            date_from: - дата "с"
            date_to: - дата "по"
            source: откуда подгружены данные
            quantity: количество подгруженных вакансий
            error: ошибка

        Returns:
             None
        """
        cls.__set_db()
        created_at: str = datetime.now().strftime('%Y%m%d %H:%M:%S')
        fields = [
            'user_id',
            'text',
            'date_from',
            'date_to',
            'source',
            'quantity',
            'error',
            'created_at'
        ]
        log_query = Query(
            user_id=cls.user_id,
            text=text,
            date_from=date_from,
            date_to=date_to,
            source=source,
            quantity=quantity,
            error=error,
            created_at=created_at
        )
        cls.session.add(log_query)
        cls.session.commit()

