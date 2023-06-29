import json
import math

import requests
from datetime import timedelta, date, datetime

from job_api.DB import DB

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
    db = None
    user_id = 0

    @classmethod
    def set_db(cls):
        if cls.db is None:
            cls.db = DB()

    @classmethod
    def get_hh_list(cls, text: str, area: str, period: int = 5) -> int:
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

        result = requests.get(HH_URL, params)
        if not result.ok:
            cls.log_query(
                text=text,
                date_from=date_from,
                date_to=date_to,
                source=source,
                quantity=0,
                error="Error get_hh_list can't load data"
            )
            return -1
        vacancies = result.json()['items']
        cls.save_hh(vacancies)
        pages = result.json()['pages']
        num_saved = 0
        for page in range(1, pages):
            params['page'] = page
            result = requests.get(HH_URL, params)
            if result.ok:
                vacancies = result.json()['items']
                num_saved += cls.save_hh(vacancies)
        cls.log_query(
            text=text,
            date_from=date_from,
            date_to=date_to,
            source=source,
            quantity=num_saved,
            error=""
        )
        return num_saved

    @staticmethod
    def get_hh_one(vacancy_id: int) -> bool:
        pass

    @classmethod
    def save_hh(cls, vacancies: dict) -> int:
        cls.set_db()
        num_saved = 0
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
            print(f"Emp: {type(vacancy['employer'])}")
            if 'employer' in vacancy:
                if 'id' in vacancy['employer']:
                    employer_id = vacancy['employer']['id']
                else:
                    employer_id = None
            else:
                employer_id = None
            values = (
                'hh',
                vacancy['id'],
                vacancy['name'],
                vacancy['area']['name'],
                salary_from,
                salary_to,
                salary_currency,
                vacancy['type']['name'],
                address_city,
                address_raw,
                address_metro,
                vacancy['published_at'],
                vacancy['alternate_url'],
                vacancy['url'],
                employer_id,
                vacancy['snippet']['requirement'],
                vacancy['snippet']['responsibility'],
                vacancy['experience']['name'],
                vacancy['employment']['name']
            )
            where = f"source_id='{vacancy['id']}'"
            cls.db.update_or_insert_one('vacancies', cls.fields, values, where)
            num_saved += 1
        return num_saved

    @classmethod
    def get_trud_vsem_list(cls, text: str, area: str, period: int = 5):
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
        print(f'Params: {params}')
        result = requests.get(TRUD_VSEM_URL, params)
        if not result.ok:
            return "Error get_trud_vsem_list can't load data"
        vacancies = result.json()['results']['vacancies']
        num_loaded += cls.save_trud_vsem(vacancies)
        total = result.json()['meta']['total']
        print(result.json()['meta'])
        pages = math.ceil(total / limit)
        print(f'Pages: {pages}')
        for page in range(1, pages):
            # Странно, но offset считают так
            params['offset'] = page  # (page - 1) * limit + 1
            print(params)
            result = requests.get(TRUD_VSEM_URL, params)
            if 'results' in result.json():
                vacancies = result.json()['results']['vacancies']
                num_loaded += cls.save_trud_vsem(vacancies)
            else:
                print(f"No results in {result.json()}")
        cls.log_query(
            text=text,
            date_from=date_from,
            date_to=date_to,
            source=source,
            quantity=num_loaded,
            error=""
        )
        return num_loaded



    @classmethod
    def save_trud_vsem(cls, vacancies: list) -> int:
        cls.set_db()
        num_saved = 0
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
            values = (
                'trudvsem',
                vacancy['id'],
                vacancy['job-name'],
                region,
                vacancy['salary_min'],
                vacancy['salary_max'],
                vacancy['currency'][:3],
                '?',
                None,
                address_raw,
                None,
                vacancy['creation-date'],
                vacancy['vac_url'],
                f"TRUD_VSEM_URL/vacancy/{vacancy['company']['companycode']}/{vacancy['id']}",
                vacancy['company']['companycode'],
                f"{vacancy['requirement']['education']}/{qualification}",
                vacancy['duty'],
                vacancy['requirement']['experience'],
                vacancy['employment']
            )
            where = f"source_id='{vacancy['id']}'"
            cls.db.update_or_insert_one('vacancies', cls.fields, values, where)
            num_saved += 1
        return num_saved

    @classmethod
    def log_query(
            cls,
            text: str,
            date_from: date,
            date_to: date,
            source: str,
            quantity: int,
            error: str = '',
    ):
        cls.set_db()
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
        values = (
            cls.user_id,
            text,
            date_from,
            date_to,
            source,
            quantity,
            error,
            created_at
        )
        cls.db.insert('queries', fields, values)
