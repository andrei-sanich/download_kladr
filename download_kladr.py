import requests
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os
import configparser
import shutil


config = configparser.ConfigParser()
config.read('config.ini')

url = config['URLS']['URL']
url_kladr_7z = config['URLS']['URL_KLADR_7Z']
url_kladr_arj = config['URLS']['URL_KLADR_ARJ']
directory = config['DIRECTORY']['DIR']


def get_html(url):

    user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'}
    response = requests.get(url, headers=user_agent).text
    return response


def get_dates(html):

    pattern_date = r'\d\d.\d\d.\d\d\d\d'
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', {'class': 'text_block'})
    date_pub_str = re.search(pattern_date, content.find('p', {'class': 'gray'}).text).group()
    date_pub = datetime.date(datetime.strptime(date_pub_str, '%d.%m.%Y'))
    date_actual_str = re.search(pattern_date, content.find('span', {'class': 'gray'}).text).group()
    date_actual = datetime.date(datetime.strptime(date_actual_str, '%d.%m.%Y'))
    date_today = datetime.date(datetime.now())
    return [date_pub, date_actual, date_today]    


def check_dates(*dates):
    
    date_pub, date_actual, date_today = dates[0]
    if date_pub == date_today or date_actual == date_today:
        return True


def create_subdir(directory, date_today):

    path = directory + str(date_today)
    try:
        os.mkdir(path)
        return path
    except OSError:
        print('Ошибка при создании директории {}'.format(path))


def download_kladr(path):

    urllib.request.urlretrieve(url_kladr_7z, path + '/BASE.7z')
    urllib.request.urlretrieve(url_kladr_arj, path + '/BASE.arj')
    return True


def remove_oldest_subdir(path):

    all_subdirs = [os.path.join(path, _dir) for _dir in os.listdir(path)]
    oldest_subdir = min(all_subdirs, key=os.path.getmtime)
    shutil.rmtree(oldest_subdir, ignore_errors=True) 


def write_msg_txtfile(date_today):

    with open('log.txt', 'a') as f:
        f.write('Базы КЛАДР по состоянию на {} скачаны и сохранены.\n'.format(date))


def main():

    dates = get_dates(get_html(url))
    if check_dates(dates):
        download_kladr(create_subdir(directory, dates[2]))
        remove_oldest_subdir(directory)
        write_msg_txtfile(dates[2])


if __name__  == '__main__':
    main()