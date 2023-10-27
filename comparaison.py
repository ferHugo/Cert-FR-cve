from pathlib import Path
import json
import re
import argparse
import pylightxl as xl
import os
from datetime import datetime

# os.remove("output.xlsx")
regex_cve = re.compile(r'CVE-\d{4}-\d{4,}')
file_path = "./data/cert_fr_data.json"


def find_by_cert_fr(data, reference):
    for d in data:
        if d["Référence"] == reference.strip():
            for cve in d["CVEs"]:
                cve_match = regex_cve.search(cve["Text"])
                if cve_match:
                    cve_name = cve_match.group(0)
                    return cve_name, cve["Link"][0]
                    #print(f'{cve_name}. Lien: {cve["Link"][0]}')

def find_by_cve(data, reference):
    results = []
    for d in data:
        for cve in d["CVEs"]:
            cve_match = regex_cve.search(cve["Text"])
            if cve_match:
                cve_name = cve_match.group(0)
                if cve_name.upper() == reference.strip().upper():
                    results.append(d)

    # Trie les résultats par date dans l'ordre décroissant
    sorted_results = sorted(results, key=lambda x: datetime.strptime(x["Date"], '%d/%m/%Y'), reverse=True)

    # Retourne seulement le plus récent
    if sorted_results:
        return [sorted_results[0]]
        print(sorted_results)
    else:
        return []

def open_data_file(path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data

def extractor():
    choice = input("\n\nQue souhaitez vous faire ?\n\t1 - Lister les CVE d'un avis Cert-FR\n\t2 - Lister les avis Cert-FR qui traitent une CVE\n\t3 - Matching dans un fichier\n\t4 - Quitter\n\n")

    if choice == "4":
        return
    with open(file_path, 'r') as file:
        data = json.load(file)
        if choice == "1":
            ref = input("Veuillez renseigner la référence Cert-FR à rechercher : ")
            
            extractor()
        if choice == "2":
            ref = input("Veuillez renseigner la CVE à rechercher : ")
            results = []
            for d in data:
                for cve in d["CVEs"]:
                    cve_match = regex_cve.search(cve["Text"])
                    if cve_match:
                        cve_name = cve_match.group(0)
                        if cve_name.upper() == ref.strip().upper():
                            results.append(d)
            if not results:
                print(f"Aucun avis Cert-FR trouvé pour la CVE {ref}.")
            else:
                for r in results:
                    print(r["Référence"])

                complete = input("Voulez-vous plus d'information ? (oui/non) : ")
                if complete.upper() == "OUI":
                    for r in results:
                        print(json.dumps(r, indent=4, ensure_ascii=False))
                elif complete.upper() != "NON" and complete.upper() != "OUI":
                    print("Option invalide : " + complete)

                    
            extractor()
        if choice == '3':

            file = input("Chemin du fichier (/root∕Cert-FR/test.xlsx):")
            main_sheet = input("Nom de la feuille principale : ")
            source_column = input("Numéro de la colonne contenant les CVE (a=1, b=2, ...): ")
            destination_column = input("Numéro de la colonne de destination (a=1, b=2, ...): ")
        
            db = xl.readxl(fn=file)
            colonnes_cves = db.ws(ws=main_sheet).col(col=int(source_column))
            destination = db.ws(ws=main_sheet).col(col=int(destination_column))

            i = 0            
            for colonne_cve in colonnes_cves:
                if i < 0:
                    continue
                if type(colonne_cve) == list:
                    avis = []
                    for cve in colonne_cve:
                        cert_fr = find_by_cve(data, cve)
                        tmp = []
                        for avis_item in cert_fr:
                            tmp.append(avis_item["Référence"])
                        avis.extend(tmp)
                    reference_avis = '\n'.join(avis)
                    destination[i] = reference_avis
                    
                if "NO" in colonne_cve or "Non" in colonne_cve:
                    destination[i] = 'Aucun Avis'
                cert_fr = find_by_cve(data, colonne_cve)
                tmp = []                
            
                for avis_item in cert_fr:
                    tmp.append(avis_item["Référence"])
                result = '\n'.join(tmp)
                db.ws(ws=main_sheet).update_index(row=i+1, col=int(destination_column), val=result)
                i += 1
                print(i)
            
            xl.writexl(db=db, fn="sortie.xlsx")


extractor()
