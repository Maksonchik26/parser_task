from dataclasses import dataclass
from dataclass_csv import DataclassWriter
from bs4 import BeautifulSoup
import requests


"""
В примере привел 120 записей с первых четырех страниц категории,
но скрипт парсит всю категорию товаров, которые в наличии
"""


@dataclass
class Product:
    id: int
    name: str
    link: str
    regular_price: int | float
    promo_price: int | float | None
    brand: str


# Main code
BASE_URL = "https://online.metro-cc.ru"
products_list = []
page = 1
while True:
    html = requests.get(f"https://online.metro-cc.ru/category/sladosti-chipsy-sneki/konfety-podarochnye-nabory?in_stock=1&page={page}").text
    soup = BeautifulSoup(html)
    print("Number of page:", page)
    if soup.find_all("div", class_="product-card__content"):
    # cycle for each product
        for i, card in enumerate(soup.find_all("div", class_="product-card__content")):

            # Promo price
            promo_price_block = card.find("div", class_="product-unit-prices__actual-wrapper")
            promo_price_rub = promo_price_block.find("span", class_="product-price__sum-rubles").text

            try:
                promo_price_penny = promo_price_block.find("span", class_="product-price__sum-penny").text
            except AttributeError:
                promo_price_penny = ""

            promo_price = promo_price_rub + promo_price_penny


            # Regular price
            regular_price_block = soup.find_all("div", class_="product-unit-prices__old-wrapper")[i]
            try:
                regular_price_rub = regular_price_block.find("span", class_="product-price__sum-rubles").text
                try:
                    regular_price_penny = regular_price_block.find("span", class_="product-price__sum-penny").text
                    regular_price = regular_price_rub + regular_price_penny
                except AttributeError:
                    regular_price_penny = ""
                    regular_price = regular_price_rub
            except AttributeError:
                regular_price = promo_price
                promo_price = None

            # Link
            product_link = BASE_URL + card.find("a", class_="product-card-photo__link reset-link").get("href")

            # Name
            product_name = card.find("a", class_="product-card-name reset-link catalog-2-level-product-card__name style--catalog-2-level-product-card").text.strip()

            # Product page
            product_html = BeautifulSoup(requests.get(product_link).text)

            # Article (id) and brand
            product_id = product_html.find("p", class_="product-page-content__article").text.split(":")[1].strip()
            product_brand = product_html.find_all("a", class_="product-attributes__list-item-link reset-link active-blue-text")[2].text.strip()

            products_list.append(Product(
                id=int(product_id),
                name=product_name,
                link=product_link,
                regular_price=regular_price,
                promo_price=promo_price,
                brand=product_brand)
            )
            print(Product(id=int(product_id), name=product_name, link=product_link, regular_price=regular_price, promo_price=promo_price, brand=product_brand))
    else:
        break

    page += 1


with open("parsing_data.csv", "w") as file:
    writer = DataclassWriter(file, products_list, Product)
    writer.write()
