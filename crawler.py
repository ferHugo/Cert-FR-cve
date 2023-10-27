import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import multiprocessing
import json
import scraper
import time
from datetime import datetime
import os

multiprocessing.set_start_method('fork', True)

num_processes = 4
max_retries = 5
retry_delay = 1
max_connections = 10
idle_delay = 0.5

last_article_file = '/root/Cert-FR/last_article.json'
last_article = None
if os.path.exists(last_article_file):
    with open(last_article_file, 'r') as f:
        last_article = json.load(f)
else:
    last_article = None


def scrape_page(page_num):
    if page_num == 1:
        url = "https://www.cert.ssi.gouv.fr/avis/"
    else:
        url = f"https://www.cert.ssi.gouv.fr/avis/page/{page_num}/"
    print(f"Scraping page {page_num}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article", class_=["item", "cert-avis", "open"])[:10]
    data = []
    tmp = 0
    for article in articles:
        num_retries = 0
        url_article = "https://www.cert.ssi.gouv.fr" + article.find("div", class_=["item-title"]).find("a").get_attribute_list(key="href")[0]
        ref_article = article.find("span", class_=["item-ref"]).get_text()
        if ref_article == last_article:
            return data, True
        while num_retries < max_retries:
            try:
                time.sleep(idle_delay)
                tmp = scraper.scraper(url_article)
                if tmp:
                    data.append(tmp)
                    break
            except IndexError:
                print(url_article)
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la récupération de la page {url}: {str(e)}")
                time.sleep(retry_delay)
                num_retries += 1
            except Exception as e:
                print(e)
    return data, False

if __name__ == '__main__':
    num_pages = 1395
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    final = []
    for page_number in range(1, num_pages+1):
        articles, last_article_found = scrape_page(page_number)
        final.extend(articles)
        if last_article_found:
            break
    if len(final) == 0:
        print("Pas de nouveaux avis depuis le dernier lancement.")
        with open(f"/root/Cert-FR/last_article.json", "w") as f:
            json.dump(last_article, f)
        exit()
    else:
        print(f"{len(final)} articles ajoutés.")
    with open(last_article_file, 'w') as f:
        json.dump(final[0]["Référence"], f)
    with open(f"/root/Cert-FR/data/{date}.json", "w") as f:
        json.dump(final, f, ensure_ascii=False)
