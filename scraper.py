from bs4 import BeautifulSoup
import requests
import re
import json


def transform_date(string):
    months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    data = string.split(' ')
    month_number = 0
    for month in months:
        month_number+=1
        if data[1].lower() == month.lower():
            data[1] = str(month_number)
            return "/".join(data)

def get_element_text_by_class(soup, element_type, class_name):
    return soup.find(element_type, {"class": class_name}).get_text().strip()

def scraper(url):
    data = {
        "Date de publication": None,
        "Date": None,
        "Référence": None,
        "Titre": None,
        "Date de première version": None,
        "Date de la dernière version": None,
        "Source(s)": None,
        "Pièce(s) jointe(s)": None,
        "Risque(s)": [],
        "Systèmes affectés": [],
        "Résumé": None,
        "Solution": None,
        "Documentation": [],
        "CVEs": [],
        "Gestion détaillée du document": None
    }
    print(url)
    page = requests.get(url, )
    page.encoding = 'utf-8'
    soup = BeautifulSoup(page.text, 'html.parser')

    publication_date_full_text = get_element_text_by_class(soup, 'div', 'row meta-pub-date')[3:]
    publication_date_time = transform_date(publication_date_full_text)
    data["Date de publication"] = publication_date_full_text
    data["Date"] = publication_date_time
    

    table = soup.find('table')
    trs = table.find_all('tr')
# Cette boucle nous a servi à comprendre la structure de donnée de la table "avis meta data"
#    for tr in trs:
#        td = tr.find_all('td')
#        print(td[1].get_text())

    data["Référence"] = trs[0].find_all('td')[1].get_text()
    data["Titre"] = trs[1].find_all('td')[1].get_text()
    data["Date de première version"] = trs[2].find_all('td')[1].get_text()

    if not soup.find("section", {"class": "article-content"}):
        return data

    data["Date de la dernière version"] = trs[3].find_all('td')[1].get_text()
    data["Source(s)"] = trs[4].find_all('td')[1].get_text().split('\r\n')
    data["Pièce(s) jointe(s)"] = trs[5].find_all('td')[1].get_text()

    data_risk = soup.find('h2', text = re.compile("Risque"))
    if data_risk:
        data_risk = data_risk.find_next()
        if data_risk.name == 'ul':
            lis = data_risk.find_all('li')
            for li in lis:
                data["Risque(s)"].append(li.get_text())
        else:
            data["Risque(s)"].append(data_risk.get_text())


    affected_systems = soup.find('h2', text=re.compile("Système"))
    if affected_systems:
        affected_systems = affected_systems.find_next()
        if affected_systems.name == 'ul':
            lis = affected_systems.find_all('li')
            for li in lis:
                data["Systèmes affectés"].append(li.get_text())
        else:
            data["Systèmes affectés"].append(affected_systems.get_text())

    digest = soup.find('h2', text=re.compile("Résumé"))
    if digest:
        digest = digest.find_next().get_text()
    else:
        digest = ""
    data["Résumé"] = digest

    digest = soup.find('h2', text=re.compile("Solution"))
    if digest:
        digest = digest.find_next().get_text()
    else:
        digest = ""
    data["Solution"] = digest

    digest = soup.find('h2', text=re.compile("Documentation"))
    if digest:
        digest = digest.find_next()
        if digest.name == 'ul':
            lis = digest.find_all('li')
            for li in lis:
                title = li.get_text().split(':')[0].strip()
                a = li.find_all('a')
                if not a:
                    continue
                links = []
                for at in a:
                    link = at.get_attribute_list(key="href")[0]
                    links.append(link)
                doc_data = {"Text": title, "Link": links}
                if not "CVE" in li.get_text():
                    data["Documentation"].append(doc_data)
                else:
                    data["CVEs"].append(doc_data)
        else:
            data["Documentation"].append(digest.get_text())

    digest = get_element_text_by_class(soup, "section", "article-footer")
    data["Gestion détaillée du document"] = digest.split("Gestion détaillée du document")[1].replace('\n', ' ').strip()[3:]
    return data




#scraper("https://www.cert.ssi.gouv.fr/avis/CERTFR-2017-AVI-417/")

#print(json.dumps(data, indent=4))
#print(data)