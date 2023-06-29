# This is a sample Python script.
from job_api.RemoteData import RemoteData


if __name__ == '__main__':
    num_saved = RemoteData.get_hh_list('python', area='', period=2)
    num_saved += RemoteData.get_trud_vsem_list('python', area='', period=5)
    print(f'Подгружено: {num_saved}')
