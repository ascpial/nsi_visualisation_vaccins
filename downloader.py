""" Ce fichier est destiné au téléchargement automatique du fichier CSV
Il est mit à part pour plus de clartée
"""

DATASET_ID = "6010206e7aa742eb447930f7"
API_SCHEME = "https://www.data.gouv.fr/api/2/datasets/{}/resources/?page=1&type=main&page_size=6"

PROXY = {}

# Importations nécessaire pour le typing
from typing import Any, Dict, List

# Importation des modules nécessaires au téléchargement
import urllib.request as request
import ssl # utilisé pour stopper l'erreur de SSL sur le réseau du lycée

# Importation du module nécessaire au traitement des informations du serveur
import json

# Importation des modules nécessaires à la gestion des anciens fichiers
import glob
import os

# Un plus joli output :)
from utils import colors

# Paramétrage du proxy pour le réseau du lycée
if False:
    proxy_support = request.ProxyHandler(
        {
            'http' : 'http://172.19.255.254:3128/',
            'https' : 'https://172.19.255.254:3128/',
        }
    )
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_file() -> Dict[str, Any]:
    with request.urlopen(
        API_SCHEME.format(DATASET_ID),
        context=ctx,
    ) as response:
        raw_json = response.read() # on lit la réponse du serveur de data.gouv.fr
        data = json.loads(raw_json)["data"] # on récupère les fichiers disponible sur le jeu de données
    target_file = None
    for file in data: # on cherche le fichier qui nous intéresse
        if file['title'].startswith("vacsi-s-a-reg-") and file['title'].endswith(".csv"):
            # on a trouvé le fichier qui nous intéresse
            target_file = file
    assert target_file is not None, "Impossible de récupérer les informations du serveur"
    return target_file

def download_file(file: Dict[str, Any]):
    url = file['url']
    with request.urlopen(url, context=ctx) as response, open('./'+file['title'], 'bw') as file:
        file.write(
            response.read()
        )

def start_download() -> str:
    """Télécharge automatiquement le fichier depuis data.gouv.fr"""
    old_files = glob.glob("vacsi-s-a-reg-*.csv")
    print(f"Téléchargement...", end=" ", flush=True)
    new_file = get_file()
    old_files = [filename for filename in old_files if filename != new_file['title']]
    download_file(new_file)
    print(f"{colors['fg']['green']}Fait{colors['reset']}")
    if len(old_files) > 0:
        print("Des anciens fichiers ont étés trouvés.")
        response = input(f"Voulez vous les garder ({colors['fg']['green']}O{colors['reset']}/{colors['fg']['red']}n{colors['reset']}) ? ")
        if response.lower() == "n":
            for filename in old_files:
                os.remove(filename)
    return new_file['title']

# pour télécharger manuellement lancez ce programme directement
if __name__ == "__main__":
    start_download()
