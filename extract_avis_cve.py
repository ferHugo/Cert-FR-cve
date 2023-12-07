from pathlib import Path
import json
import re
import argparse
import pylightxl as xl
import os
from datetime import datetime
import csv
import pandas as pd
import pyfiglet

ascii_banner = pyfiglet.figlet_format("Script CERT-FR")
print(ascii_banner)

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
                
#os_filters pour filtrer sur les OS (debian,RHEL,centos)
def find_by_cve(data, reference, os_filters=None):
    results = []
    for d in data:
        for cve in d["CVEs"]:
            cve_match = regex_cve.search(cve["Text"])
            if cve_match:
                cve_name = cve_match.group(0)
                if cve_name.upper() == reference.strip().upper():
                    if os_filters is None or any(os_filter.upper() in d["Systèmes affectés"][0].upper() for os_filter in os_filters):
                        results.append(d)

    sorted_results = sorted(results, key=lambda x: datetime.strptime(x["Date"], '%d/%m/%Y'), reverse=True)

    if sorted_results:
        return [sorted_results[0]]
    else:
        return []

    
def export_to_csv(data, file, main_sheet, source_column, destination_column):
    csv_data = []  
    header = ["CVE", "Avis", "Titre"]
    csv_data.append(header)

    db = xl.readxl(fn=file)
    src = db.ws(ws=main_sheet).col(col=int(source_column))
    src = [item.split('\n') if '\n' in item else [item] for item in src]
    numero_ligne = 0
    csv_data = []

    # Numéro où commence le script
    
    for cve_list in src:
        
        if numero_ligne < 0:
            continue
        if type(cve_list) == list:
            for cve_item in cve_list:
                cert_fr = find_by_cve(data, cve_item)
                for cve_data in cert_fr:
                    
                    if isinstance(cve_data, dict):
                        reference = cve_data.get("Référence", "NR")
                        title = cve_data.get("Titre", "NR")
                        row_data = [cve_item, reference, title]
                        csv_data.append(row_data)
                    elif isinstance(cve_data, list):
                        for item in cve_data:
                            reference = item.get("Référence", "NR")
                            title = item.get("Titre", "NR")
                            row_data = [cve_item, reference, title]
                            csv_data.append(row_data)
                    else:
                        reference = "NR"
                        title = "NR"
                        row_data = [cve_item, reference, title]
                        csv_data.append(row_data)
                    numero_ligne += 1

    # Ajout pour afficher les données exportées
    print("Données à exporter :")
    for row in csv_data:
        print(row)
    # Formate la date et l'heure comme tu le souhaites (par exemple, YYYY-MM-DD_HH-MM-SS)
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Utilise le nom de fichier formaté lors de l'export
    with open("csv/export.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Écrire l'en-tête
        writer.writerow(['CVE', 'Avis', 'Titre'])
        # Écrire les données
        writer.writerows(csv_data)
        
    print("Export CSV réussi!")

def ouverture_fichier(path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data
    
def creation_excel(data, file, main_sheet, source_column, destination_column):
    db = xl.readxl(fn=file)
    src = db.ws(ws=main_sheet).col(col=int(source_column))
    dest = db.ws(ws=main_sheet).col(col=int(destination_column))
    dest_name = db.ws(ws=main_sheet).col(col=int(destination_column) + 1)
    numero_ligne = 0
    
    for cve_list in src:
        if numero_ligne < 0:
            continue
        if type(cve_list) == list:
            avis_references = []
            avis_names = []
            for cve_item in cve_list:
                cert_fr = find_by_cve(data, cve_item)
                reference = []
                names = []
                for cve_data in cert_fr:
                    if isinstance(cve_data, dict):
                        reference.append(cve_data.get("Référence", "NR"))
                        names.append(cve_data.get("Gestion détaillée du document", "NR"))
                    elif isinstance(cve_data, list):
                        reference.extend(item.get("Référence", "NR") for item in cve_data)
                        names.extend(item.get("Gestion détaillée du document", "NR") for item in cve_data)
                    else:
                        reference.append("NR")
                        names.append("NR")
                avis_references.extend(reference)
                if names:
                    avis_names.append(names[1])  # On prend le premier nom de l'avis
                else:
                    avis_names.append("NR")
            sr = '\n'.join(avis_references)
            sr_name = '\n'.join(avis_names)
            dest[numero_ligne] = sr
            dest_name[numero_ligne] = sr_name

        if "NO" in cve_list or "Non" in cve_list:
            dest[numero_ligne] = 'NR'
            dest_name[numero_ligne] = 'NR'
        cert_fr = find_by_cve(data, cve_list)
        reference = []
        names = []

        for cve_data in cert_fr:
            if isinstance(cve_data, dict):
                reference.append(cve_data.get("Référence", "NR"))
                names.append(cve_data.get("Titre", "NR"))
            elif isinstance(cve_data, list):
                reference.extend(item.get("Référence", "NR") for item in cve_data)
                names.extend(item.get("Titre", "NR") for item in cve_data)
            else:
                reference.append("NR")
                names.append("NR")

        result = '\n'.join(reference)
        result_name = '\n'.join(names)
        db.ws(ws=main_sheet).update_index(row=numero_ligne+1, col=int(destination_column), val=result)
        db.ws(ws=main_sheet).update_index(row=numero_ligne+1, col=int(destination_column) + 1, val=result_name)
        numero_ligne += 1
        print(numero_ligne)

    # Formate la date et l'heure comme tu le souhaites (par exemple, YYYY-MM-DD_HH-MM-SS)
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Utilise le nom de fichier formaté lors de l'export
    xl.writexl(db=db, fn=f"xlsx/{formatted_datetime}_cve_et_avis.xlsx")
    print("fin")

def extractor():
    choice = input("\n\nQue souhaitez-vous faire ?\n\t1 - Lister les CVE d'un avis Cert-FR\n\t2 - Lister les avis Cert-FR qui traitent une CVE\n\t3 - Matching dans un fichier\n\t4 - Voulez-vous exporter les données sous format CSV?\n\t5 - Quitter\n\n")

    if choice == "5":
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

                complete = input("Voulez-vous plus d'informations ? (oui/non) : ")
                if complete.upper() == "OUI":
                    for r in results:
                        print(json.dumps(r, indent=4, ensure_ascii=False))
                elif complete.upper() != "NON" and complete.upper() != "OUI":
                    print("Option invalide : " + complete)

            extractor()

        if choice == '3':
            #chemin ou se trouve le fichier 
            chemin = "/root/Cert-FR/"
            fichier = input("Nom du fichier: ")
            format = ".xlsx"
            file = chemin + fichier + format
            main_sheet = input("Nom de la feuille principale : ")
            source_column = input("Numéro de la colonne contenant les CVE (a=1, b=2, ...): ")
            destination_column = input("Numéro de la colonne de destination (a=1, b=2, ...): ")
            creation_excel(data, file, main_sheet, source_column, destination_column)
        
        if choice == '4':
            chemin = "/root/Cert-FR/"
            fichier = input("Nom du fichier: ")
            format = ".xlsx"
            file = chemin + fichier + format
            main_sheet = input("Nom de la feuille principale : ")
            source_column = input("Numéro de la colonne contenant les CVE (a=1, b=2, ...): ")
            destination_column = input("Numéro de la colonne de destination (a=1, b=2, ...): ")
            export_to_csv(data, file, main_sheet, source_column, destination_column)

extractor()
