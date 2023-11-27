# Projet de Matching d'Avis CVE - Cert-FR

Ce projet propose un script en Python permettant de faire correspondre des avis du Cert-FR avec des Common Vulnerabilities and Exposures (CVE). Le script extrait les données pertinentes des avis du Cert-FR, filtre les CVE associées, et les organise dans un fichier Excel.

**Fonctionnalités principales** :

- Lister les CVE d'un avis Cert-FR : Le script permet de saisir une référence d'avis Cert-FR et retourne les CVE associées.

- Lister les avis Cert-FR pour une CVE donnée : L'utilisateur peut fournir le numéro de CVE, et le script affiche les avis Cert-FR pertinents.

- Matching dans un fichier Excel : Le script prend en entrée un fichier Excel avec une colonne de CVE, recherche les avis Cert-FR correspondants, et génère un fichier de sortie Excel avec les résultats.

## **Installation**

Pour exécuter le script, suivez ces étapes :

* Installer Python 3 *: Téléchargez et installez Python 3.

Cloner le projet : Clonez ce projet depuis GitHub en utilisant la commande suivante :

bash

    git clone https://github.com/ferHugo/Cert-FR-cve.git

Installer les dépendances : Accédez au répertoire du projet et installez les dépendances en exécutant la commande suivante dans votre terminal :

bash

    pip install -r requirements.txt

## **Utilisation**

Exécutez le merger pour scrape les avis du CERT-FR (insére les données dans un json):

bash

    python3 merger.py

Exécutez le script en utilisant la commande suivante :

bash

    python3 extract_avis_cve.py

Choisissez l'option correspondant à l'action souhaitée (Lister les CVE, Lister les avis, Matching dans un fichier).

Suivez les instructions à l'écran pour fournir les références ou fichiers nécessaires.

Consultez les résultats dans le fichier de sortie Excel généré.

## **Exemples**


![ On donne une liste de cve ](/images/1.png)
![ L'Excel une fois le script qui a tourné ](/images/2.png)





