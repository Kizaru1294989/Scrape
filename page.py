from urllib.parse import ParseResult, urlparse
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import urllib.request as t
import json
import pymongo
from bson import json_util
import streamlit as st
import numpy as np

def Insert(number,dictionary):
    client = pymongo.MongoClient('mongodb://localhost:27017')
    mydb = client['Scrape']
    collection = mydb['s']
    collection.insert_one(json_util.loads(json_util.dumps(dictionary)))
    if number == 48:
        print('OVER')
        df = pd.DataFrame(list(collection.find()))
        views_per_user = df.groupby('Pseudo')['nombre de vues'].sum()
        st.bar_chart(views_per_user)
        df = df.explode('type')
        views_per_type = df.groupby('type')['nombre de vues'].sum()
        st.bar_chart(views_per_type)
        st.stop()

def clear_data(data): 
    # extraire les données sans les tags html
    clear_data = []
    for element in data:
        clear_data.append(element.text)
    return clear_data

def extract_href(string):
    # extraire le href du string
    debut = 'href="'
    fin = '"'
    split_string = string.split(" ")
    lien = split_string[3]
    href = (lien.split(debut))[1].split(fin)[0]
    return href

def extract_content(href_titre):
    # collection des données
    page = t.urlopen(href_titre)
    soup = bs(page, "html.parser")
    content_div = soup.find_all('div', {'class': 's-prose js-post-body'})
    language_div = soup.find_all('div', {'class':'d-flex ps-relative fw-wrap'})
    account_info_div = soup.find_all('div', {'class':'user-info'})
    content = clear_data(content_div)
    language = clear_data(language_div)
    account_info = clear_data(account_info_div)
    content = [s.replace("\n", "") for s in content]
    content = [s.replace("\"", "") for s in content]
    language = [s.replace("\n", "") for s in language]
    account_info = [s.replace("\n", "") for s in account_info]
    account_info = [s.replace("\r", "") for s in account_info]
    return content, language, account_info

def save_to_json(page_number, Views, Names, Titles, Hrefs):
    # mettre toutes les donnés dans des arbres JSON
    with open('page-' + str(page_number) + '.json', "w", encoding="utf-8") as f:
        for index, title in enumerate(Titles):
            href_titre = "https://stackoverflow.com" + Hrefs[index]
            print(" NUMBER = "+str(index + 1) + "/48  HREF = " + href_titre)
            content, language, account_info = extract_content(href_titre)
            dictionary = {
                'number': str(index + 1) + "/48",
                'Pseudo': Names[index],
                'titre': title,
                'href': Hrefs[index],
                'nombre de vues' : Views[index],
                'type': str(language),
                'github_score_time': account_info,
                'contenus': content,
            }
            json.dump(dictionary, f, ensure_ascii=False, indent=4)
            Insert(index + 1 , dictionary)
            print("Data inserted in MongoDB!")         

def scrape():
    # function principale qui servira de loop pour scraper toutes les pages et leur contenus
    page_number = 0
    while page_number < 10: # nombres de pages à scrap
        page_number += 1
        print("Page " + str(page_number) + "/10")
        link = "https://stackoverflow.com/questions?tab=newest&page=" + str(page_number)
        page = t.urlopen(link)
        soup = bs(page, "html.parser")
        views_span = soup.find_all('span', {'class': 's-post-summary--stats-item-number'})
        pseudo_div = soup.find_all('div', {'class': 's-user-card--link d-flex gs4'})
        titles_h3 = soup.find_all('h3', {'class': 's-post-summary--content-title'})
        titles_h3.pop(0)
        titles_h3.pop(0)
        views = clear_data(views_span)
        titles = clear_data(titles_h3)
        names = clear_data(pseudo_div)
        names = [s.replace("\n", "") for s in names]
        hrefs = [extract_href(str(title)) for title in titles_h3]
        save_to_json(page_number, views, names, titles, hrefs)
    print("Scrap over ")
