import requests
import lxml
import csv
import time
import json
from bs4 import BeautifulSoup
from datetime import datetime


start_time = time.time()


def get_data():
    current_date = datetime.now().strftime('%d_%m_%Y_%H_%M')

    with open(f'labirint_{current_date}.csv', 'w', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file, delimiter=';', lineterminator='\n')
        writer.writerow(
            (
                'Название книги',
                'Автор',
                'Издательство',
                'Цена со скидкой',
                'Цена без скидки',
                'Размер скидки, %',
                'Наличие на складе'
            )
        )

    url = 'https://www.labirint.ru/genres/2304/?display=table&available=1'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    }
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    pages_count = int(soup.find('div', class_='pagination-numbers').find_all('a')[-1].text) # поиск последней страницы

    books_data = []
    for page in range(1, pages_count + 1):
        url = f'https://www.labirint.ru/genres/2304/?display=table&available=1&page={page}'
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        books_items = soup.find('tbody', class_='products-table__body').find_all('tr') # получение карточек

        for bi in books_items:
            book_data = bi.find_all('td')

            try:
                book_title = book_data[0].find('a').text.strip() # получение названя книги в карточке
            except:
                book_title = 'Нет названия книги'

            try:
                book_author = book_data[1].text.strip() # получение автора
            except:
                book_author = 'Нет автора'

            try:
                book_publishing = book_data[2].find_all('a') # получение издательства
                book_publishing = ': '.join([bp.text for bp in book_publishing])
            except:
                book_publishing = 'Нет издательства'

            try:
                book_new_price = int(book_data[3].find('span', class_='price-val').find('span').text.strip()\
                    .replace(' ', '')) # получение новой цены
            except:
                book_new_price = 0

            try:
                book_old_price = int(book_data[3].find('span', class_='price-gray').text.strip().replace(' ', ''))
            except:
                book_old_price = 0

            try:
                book_sale = round(100 * (1 - book_new_price / book_old_price))
            except:
                book_sale = 0

            try:
                book_status = book_data[-1].text.strip()
            except:
                book_status = 'Книги нет в наличии'

            if book_new_price:
                books_data.append(
                    {
                    'book_title': book_title,
                    'book_author': book_author,
                    'book_publishing': book_publishing,
                    'book_new_price': book_new_price,
                    'book_old_price': book_old_price,
                    'book_sale': book_sale,
                    'book_status': book_status
                    }
                )

            with open(f'labirint_{current_date}.csv', 'a', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';', lineterminator='\n')
                if book_new_price != 0:
                    writer.writerow(
                            (
                                book_title,
                                book_author,
                                book_publishing,
                                book_new_price,
                                book_old_price,
                                book_sale,
                                book_status
                            )
                        )

        print(f'Обработано страниц: {page}/{pages_count}')
        time.sleep(2)

    with open(f'labirint_{current_date}.json', 'w', encoding='utf-8') as json_file:
        json.dump(books_data, json_file, indent=4, ensure_ascii=False)


def main():
    get_data()
    finish_time = time.time() - start_time
    print(f'Затраченное на работу скрипта время: {finish_time}')


if __name__ == '__main__':
    main()
