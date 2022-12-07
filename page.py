from urllib.parse import ParseResult, urlparse
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import urllib.request as t
import json


def clear_data(str): # avoir la data sans les html tags 
    clear_projet = []
    for e, projet in enumerate(str):
        clear_projet.append(str[e].text)
    return clear_projet


def get(exemple, int):
    try:
        page = t.urlopen(exemple)
        source = bs(page, "html.parser")
        V = source.find_all('span', {'class': 's-post-summary--stats-item-number'})  # nombre de vues
        Pseudo = source.find_all('div', {'class': 's-user-card--link d-flex gs4'})   # Pseudo
        AllTitle = source.find_all('a', {'class': 's-link'})  # titre
        AllTitle.pop(0)    # .pop nous permet de retirer des strings du slice ici on supprime les 2 premiers et le dernier car ils sont vides
        AllTitle.pop(0)
        AllTitle.pop(50)
        with open('page' + str(int) + '.json', "w", encoding="utf-8") as f:
            for taille, contenus in enumerate(AllTitle):
                href = contenus['href']   #href du post
                href_titre = "https://stackoverflow.com" + str(href)
                page1 = t.urlopen(href_titre)
                question = bs(page1,"html.parser")
                tout = question.find_all('div', {'class': 's-prose js-post-body'})
                language = question.find_all('div', {'class':'d-flex ps-relative fw-wrap'}) # Languages ?
                info_compte = question.find_all('div', {'class':'user-info'}) # github compte du createur et des réponses
                Views = clear_data(V)
                titre = clear_data(AllTitle)    #data sans les html balises
                Nom = clear_data(Pseudo)
                contenu_href = clear_data(tout)
                language_clear = clear_data(language)
                compe_ifno_clear = clear_data(info_compte)
                new_list = [s.replace("\n", "") for s in Nom]  #supprimer les \n du pseudo
                new_list1 = [s.replace("\n", "") for s in contenu_href]
                new_list2 = [s.replace("\n", "") for s in titre]
                new_list3 = [s.replace("\"", "") for s in new_list1]
                new_list4 = [s.replace("\"", "") for s in new_list2]
                new_list5 = [s.replace("\n", "") for s in language_clear]
                new_list6 = [s.replace("\n", "") for s in compe_ifno_clear]
                new_list7 = [s.replace("\r", "") for s in new_list6]
                dictionary = {
                'nombre de vues' : Views[taille],
                'type':new_list5,
                'Pseudo': new_list[taille],
                'github_score_time':new_list7,
                'href': href,
                'contenus':new_list3,
                'titre': new_list4[taille],
                'number': str(taille + 1) + "/50" }
                json.dump(dictionary, f, ensure_ascii=False, indent=4)
    except:
        pass
    scrape(int)
    print("Too many http request... Please wait -_-°")  

print("Please Wait.. it will take some time")


def scrape(int):
    #page = 0
    while int < 10: # nombres de pages a scrap
        int += 1
        print(str(int)+"/"+str(10))
        link = "https://stackoverflow.com/questions?tab=newest&page=" + str(int)
        print(link)
        get(link, int)
        if int == 10:
            print("Scrap_Over")
            exit()


def allurl(name):
    reqs = requests.get(name)
    soup = bs(reqs.text, 'html.parser')

    urls = []
    for link in soup.find_all('a', href=True):
        print(link.get('href'))