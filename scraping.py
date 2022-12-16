#!/usr/bin/python3
import os
import re
import time

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome import options as chrome_options


def get_page(count = 1, headless=False):
    driver = get_driver(headless=headless)
    pages = []
    page_url = f"https://www.kubii.fr/174-raspberry-pi-4-modele-b/s-1/categories_2-cartes_systemes"
    driver.get(page_url)
    time.sleep(1)
    pages.append(driver.page_source.encode("utf-8"))
    return pages


def get_driver(headless=False):
    if headless:
        options = chrome_options.Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
    else:
        driver = webdriver.Chrome()
    return driver


def save_pages(pages):
    os.makedirs("data", exist_ok=True)
    for page in pages:
        with open(f"data/page.html", "wb") as f_out:
            f_out.write(page)


def parse_pages():
    pages_paths = os.listdir("data")
    results = pd.DataFrame()
    for page_path in pages_paths:
        with open("data/" + page_path, "rb") as f_in:
            page = f_in.read().decode("utf-8")
            results = pd.concat((results, parse_page(page)))
    return results


def parse_page(page):
    soup = BeautifulSoup(page, "html.parser").find("ul", {"class": "product_list grid row"})
    result = pd.DataFrame()
    result["Product name:"] = [
        clean_name(tag) for tag in soup.find_all(attrs={"class": "product-name"})
    ]
    result["Price (€):"] = [
        clean_price(tag) for tag in soup.find_all(attrs={"class": "price product-price"})
    ]
    result["Availability:"] = [
        clean_availability(tag) for tag in soup.find_all(attrs={"class": "button_cart button ajax_add_to_cart_button btn btn-default disabled"})
    ]
    result["Photo URL:"] = [
        clean_photo_url(tag) for tag in soup.find_all(attrs={"class": "replace-2x img-responsive"})
    ]
    result["Product URL:"] = [
        clean_product_url(tag) for tag in soup.find_all(attrs={"class": "product-name"})
    ]
    return result


def clean_price(tag):
    text = tag.text.strip()
    price = float(text.replace("€", "").replace(" ", "").replace(",", "."))
    return price


def clean_name(tag):
    text = tag.text.strip()
    return text


def clean_availability(tag):
    text = tag.text.strip()
    return text


def clean_photo_url(tag):
    url = tag.get('src')
    return url


def clean_product_url(tag):
    url = tag.find("a").get('href')
    return url


def main():
    pages = get_page()
    save_pages(pages)
    results = parse_pages()
    print(results)
    os.makedirs("datas", exist_ok=True)
    results.to_csv(r'datas/raspberry_infos.txt', header=None, index=None)


if __name__ == "__main__":
    main()
