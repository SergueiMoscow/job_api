# This is a sample Python script.
from job_api.RemoteData import RemoteData
from job_api.logger import info, debug

if __name__ == '__main__':
    num_saved = RemoteData.get_hh_list('python', area='', period=1)
    num_saved += RemoteData.get_trud_vsem_list('python', area='', period=5)
    info(f'Подгружено: {num_saved}, Добавлено: {RemoteData.inserted_records}, Заменено: {RemoteData.updated_records}')
