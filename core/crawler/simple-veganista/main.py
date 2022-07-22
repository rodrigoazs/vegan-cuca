import json
import logging
import os
import random
import time

import requests
from bs4 import BeautifulSoup

URL = "https://simple-veganista.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%m-%d %H:%M",
)


def get_soup(url):
    time.sleep(random.uniform(0, 1))
    page = requests.get(url, headers=headers)
    html = page.text
    soup = BeautifulSoup(html, "html.parser")
    return soup


def clean_href(href):
    if "/print/" in href:
        return href.split("print/")[0]
    if "/comment-page-" in href:
        return href.split("comment-page-")[0]
    return href


def get_page_info(url):
    try:
        soup = get_soup(url)
        hrefs = [
            clean_href(h["href"])
            for h in soup.find_all("a")
            if h.get("href", "").startswith(URL)
        ]
        recipe = None
        title = soup.find("h2", class_="tasty-recipes-title")
        if title:
            ingredients = soup.find("div", class_="tasty-recipes-ingredients").text
            instructions = soup.find("div", class_="tasty-recipe-instructions").text
            title = title.text
            recipe = (title, ingredients, instructions)
        return (hrefs, recipe)
    except Exception as err:
        save_status()
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
    file_path = f"data/simple-veganista/{file_name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f)


def save_status():
    status = {"to_visit": list(to_visit), "visited": list(visited)}
    with open("simple-veganista-status.json", "w", encoding="utf-8") as f:
        json.dump(status, f)


if not os.path.exists("simple-veganista-status.json"):
    to_visit = set([URL])
    visited = set()
else:
    with open("simple-veganista-status.json", "r", encoding="utf-8") as f:
        d = json.load(f)
        to_visit = set(d["to_visit"])
        visited = set(d["visited"])

while to_visit:
    url = to_visit.pop()
    file_name = url.split("/")[-2]
    file_path = f"data/simple-veganista/{file_name}.json"
    if not os.path.exists(file_path):
        hrefs, recipe = get_page_info(url)
        if recipe:
            logging.debug(f"Saving {file_path}")
            title, ingredients, instructions = recipe
            save_json_file(url, title, ingredients, instructions)
        visited = visited.union(set([url]))
        diff = set(hrefs).difference(visited)
        to_visit = to_visit.union(diff)
    else:
        logging.debug(f"Skipping {file_path}")
