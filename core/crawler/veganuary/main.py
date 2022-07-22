import json
import logging
import os
import random
import time

import requests
from bs4 import BeautifulSoup

URL = "https://veganuary.com/recipes/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%m-%d %H:%M",
)


def get_soup(url):
    time.sleep(random.uniform(0, 2))
    page = requests.get(url, headers=headers)
    html = page.text
    soup = BeautifulSoup(html, "html.parser")
    return soup


def get_recipe(url):
    try:
        soup = get_soup(url)
        title = soup.find("h1", class_="hero__title").text
        ingredients = soup.find("div", class_="recipe__ingredients").text
        preparation = soup.find("div", class_="recipe__preparation")
        method = soup.find("div", class_="recipe__method")
        desc = [p.text for p in [preparation, method] if p]
        preparation = "".join(desc)
        return title, ingredients, preparation
    except Exception as err:
        logging.debug(f"Error in {url}")
        raise err


def save_json_file(href, title, ingredients, preparation):
    json_data = {
        "href": href,
        "title": title,
        "ingredients": ingredients,
        "preparation": preparation,
    }
    file_name = href.split("/")[-2]
    file_path = f"data/veganuary/{file_name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f)


soup = get_soup(URL)
results = soup.find_all("a", class_="card__link")

for link in results:
    href = link["href"]
    soup = get_soup(href)
    recipes = soup.find_all("a", class_="card__link")
    for recipe in recipes:
        recipe_href = recipe["href"]
        file_name = recipe_href.split("/")[-2]
        file_path = f"data/veganuary/{file_name}.json"
        if not os.path.exists(file_path):
            logging.debug(f"Saving {file_path}")
            title, ingredients, preparation = get_recipe(recipe_href)
            save_json_file(recipe_href, title, ingredients, preparation)
        else:
            logging.debug(f"Skipping {file_path}")
    pagination = soup.find_all("a", class_="page-numbers")
    if pagination:
        last_page = int(pagination[-1].text)
        for page_number in range(2, last_page + 1):
            soup = get_soup("{}page/{}/".format(href, page_number))
            recipes = soup.find_all("a", class_="card__link")
            for recipe in recipes:
                recipe_href = recipe["href"]
                file_name = recipe_href.split("/")[-2]
                file_path = f"data/veganuary/{file_name}.json"
                if not os.path.exists(file_path):
                    logging.debug(f"Saving {file_path}")
                    title, ingredients, preparation = get_recipe(recipe_href)
                    save_json_file(recipe_href, title, ingredients, preparation)
                else:
                    logging.debug(f"Skipping {file_path}")

logging.debug("Finished")
