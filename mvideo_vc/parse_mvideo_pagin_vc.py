from parse_mvideo_conf_vc import headers, cookies
import requests
import json
import os
import math


def get_data():

    params = {
        'categoryId': '195',
        'offset': '0',
        'limit': '24',
        'filterParams': 'WyJ0b2xrby12LW5hbGljaGlpIiwiIiwiZGEiXQ==',
        'doTranslit': 'true',
    }

    if not os.path.exists('data'):
        os.mkdir('data')

    s = requests.Session()

    response = s.get('https://www.mvideo.ru/bff/products/listing',
                     params=params, cookies=cookies, headers=headers).json()

    total_items = response.get('body').get('total')

    if total_items is None:
        return '[!] No items :('

    pages_count = math.ceil(total_items / int(params['limit']))

    products_ids = {}
    products_description = {}
    products_prices = {}

    for i in range(pages_count):
        offset = f'{i*24}'
        params = {
            'categoryId': '195',
            'offset': offset,
            'limit': '24',
            'filterParams': 'WyJ0b2xrby12LW5hbGljaGlpIiwiIiwiZGEiXQ==',
            'doTranslit': 'true',
        }

        response = s.get('https://www.mvideo.ru/bff/products/listing',
                         params=params, cookies=cookies, headers=headers).json()

        products_ids_list = response.get('body').get('products')
        products_ids[i] = products_ids_list

        json_data = {
            'productIds': products_ids_list,
            'mediaTypes': [
                'images',
            ],
            'category': True,
            'status': True,
            'brand': True,
            'propertyTypes': [
                'KEY',
            ],
            'propertiesConfig': {
                'propertiesPortionSize': 5,
            },
            'multioffer': False,
        }

        response = requests.post('https://www.mvideo.ru/bff/product-details/list',
                                 cookies=cookies, headers=headers, json=json_data).json()
        products_description[i] = response

        params = {
            'productIds': ','.join(products_ids_list),
            'addBonusRubles': 'true',
            'isPromoApplied': 'true',
        }

        response = s.get('https://www.mvideo.ru/bff/products/prices',
                         params=params, cookies=cookies, headers=headers).json()

        material_prices = response.get('body').get('materialPrices')

        for item in material_prices:
            item_id = item.get('price').get('productId')
            item_basePrice = item.get('price').get('basePrice')
            item_salePrice = item.get('price').get('salePrice')
            item_bonus = item.get('bonusRubles').get('total')

            products_prices[item_id] = {
                'item_basePrice': item_basePrice,
                'item_salePrice': item_salePrice,
                'item_bonus': item_bonus
            }

        print(f'[+] Finished {i+1} of the {pages_count} pages')

        with open('data/1_products_ids.json', 'w', encoding='utf-8') as file:
            json.dump(products_ids, file, indent=4, ensure_ascii=False)

        with open('data/2_products_description.json', 'w', encoding='utf-8') as file:
            json.dump(products_description, file, indent=4, ensure_ascii=False)

        with open('data/3_products_prices.json', 'w', encoding='utf-8') as file:
            json.dump(products_prices, file, indent=4, ensure_ascii=False)


def get_result():
    with open('data/2_products_description.json', encoding='utf-8') as file:
        products_data = json.load(file)

    with open('data/3_products_prices.json', encoding='utf-8') as file:
        products_prices = json.load(file)

    for item in products_data.values():
        products = item.get('body').get('products')

        for item in products:
            product_id = item.get('productId')

            if product_id in products_prices:
                prices = products_prices[product_id]

            item['item_basePrice'] = prices.get('item_basePrice')
            item['item_salePrice'] = prices.get('item_salePrice')
            item['item_bonus'] = prices.get('item_bonus')
            item['item_link'] = f'https://www.mvideo.ru/products/{item.get("nameTranslit")}-{product_id}'

    with open('data/4_result.json', 'w', encoding='utf-8') as file:
        json.dump(products_data, file, indent=4, ensure_ascii=False)


def main():
    get_data()
    get_result()


if __name__ == '__main__':
    main()
