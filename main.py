"""
0: reg;
1: clage_vacsi;
2: jour;
3: n_dose1_h;
4: n_complet_h;
5: n_rappel_h;
6: n_cum_dose1_h;
7: n_cum_complet_h;
8: n_cum_rappel_h;
9: couv_dose1_h;
10: couv_complet_h;
11: couv_rappel_h;
12: n_dose1_f;
13: n_complet_f;
14: n_rappel_f;
15: n_cum_dose1_f;
16: n_cum_complet_f;
17: n_cum_rappel_f;
18: couv_dose1_f;
19: couv_complet_f;
20: couv_rappel_f;
21: n_dose1_e;
22: n_complet_e;
23: n_rappel_e;
24: n_cum_dose1_e;
25: n_cum_complet_e;
26: n_cum_rappel_e;
27: couv_dose1_e;
28: couv_complet_e;
29: couv_rappel_e
"""

# Importation des utilitaires n'étant pas en rapports avec la logique du code
from typing import Any, Callable, List, Optional, Tuple, Union

# Importation du module de lecture de base de données
import csv

# Importation du module utilisé pour la détecection automatique du fichier
import glob

# Importation du module nécessaire à la gestion du temps
import datetime

# Importation des modules nécessaires au traitement de l'image
import matplotlib.pyplot as plt
from PIL import Image

import io # nécessaire pour la conversion de l'image plot en image PIL

# des plus jolis affichages :P
from utils import colors

# On essait d'importer le module de téléchargement automatique
# Si il n'existe pas, on désactive le support pour le téléchargement
try:
    from downloader import start_download
    DOWNLOAD_SUPPORT = True
except ImportError:
    DOWNLOAD_SUPPORT = False

# On créé quelques contantes pour gérer les données
AGES = [
    ('04', "0-4"),
    ('09', "5-9"),
    ('11', "10-11"),
    ('17', "12-17"),
    ('24', "18-24"),
    ('29', "25-29"),
    ('39', "30-39"),
    ('49', "40-49"),
    ('59', "50-59"),
    ('64', "60-64"),
    ('69', "65-69"),
    ('74', "70-74"),
    ('79', "75-79"),
    ('80', "80 et +"),
]

REGIONS = {
    "01": "Guadeloupe",
    "02": "Martinique",
    "03": "Guyane",
    "04": "La Réunion",
    "11": "Ile-de-France",
    "24": "Centre-Val de Loire",
    "27": "Bourgogne-Franche-Comté",
    "28": "Normandie",
    "32": "Hauts-de-France",
    "44": "Grand Est",
    "52": "Pays de la Loire",
    "53": "Bretagne",
    "75": "Nouvelle-Aquitaine",
    "76": "Occitanie",
    "84": "Auvergne-Rhône-Alpes",
    "93": "Provence-Alpes-Côte d’Azur",
    "94": "Corse",
}

# Section de lecture de la base de données
def load_file(chemin: str) -> List[List[Any]]:
    """Charge un fichier csv et retourne la base de données

    :param chemin: L'emplacement du fichier à lire
    :type chemin: str
    :return: La base de données convertie en liste de listes
    :rtype: List[List[Any]]
    """
    with open(chemin, encoding='utf-8') as file: # ouvre le fichier en encodage utf-8 (support des accents...)
        reader = csv.reader(file, delimiter=";") # lecture du fichier csv (le séparateur est un ;)
        data = list(reader) # on convertir le lecteur en liste pour plus de praticité
    data = data[1:] # on retire les headers
    return data

def selection(data: List[List[Any]], test: Callable[[List[Any]], bool]) -> List[List[Any]]:
    """Permet d'effectuer une sélection sur une base de données

    :param data: La base de données sur laquelle effectuer l'opération
    :type data: List[List[Any]]
    :param test: Le test à effectuer. Il doit prendre en argument une liste, correspondant à la ligne sur laquelle est effectuée le test
    :type test: Callable[List[Any]]
    :return: La base de données résultante de exécution de l'opération
    :rtype: List[List[Any]]
    """
    output = [] # on créé la liste de retour vide
    for entry in data: # on regarde chaque ligne (entry) de la base de données
        if test(entry): # on effectue le test sur la ligne
            output.append(entry) # si le test est positif on ajoute la ligne à la liste de sortie
    return output

def projection(table: List[List[Any]], listeNumCol: Tuple[int]) -> List[List[Any]]:
    """Permet d'effectuer une projection sur une base de données

    :param table: La base de données avec laquelle effectuer l'opération
    :type table: List[List[Any]]
    :param listeNumCol: Contient les indices des colonnes à garder
    :type listeNumCol: Tuple[int]
    :return: La base de données résultante de l'exécution de l'opération
    :rtype: List[List[Any]]
    """
    return [[data[col] for col in listeNumCol] for data in table]

# Fonction nécessaires à l'interface avec l'utilisateur
def ask_file() -> str:
    """Demande à l'utilisateur l'emplacement du fichier csv.

    :return: Le chemin (relatif ou absolu) du fichier de base de données
    :rtype: str
    """
    chemin = input(
        f"Chemin du fichier à lire (laisser vide pour une détection automatique){' (saississez d pour le téléchargement automatique)' if DOWNLOAD_SUPPORT else ''} : {colors['fg']['yellow']}"
    )
    print(colors['reset'], end="")

    if chemin == 'd' and DOWNLOAD_SUPPORT:
        chemin = start_download()
    
    elif chemin == "": # on tente une détection automatique
        chemins = glob.glob("./vacsi-s-a-reg-*.csv")
        
        # on n'a pas trouvé de fichier
        if len(chemins) == 0:
            print(f"{colors['fg']['red']}Aucun fichier correspondant n'a été trouvé dans le répertoire actuel.{colors['reset']}")
            print(f"{colors['underline']}Merci de spécifier le chemin du fichier.{colors['reset']}")
            return ask_file() # on redemande le fichier
        
        # si il y a plusieurs fichiers qui correspondent
        elif len(chemins) > 1:
            selected = False # la boucle sera exécutée tant que selected vaut False
            while not selected:
                print("Les fichiers suivants ont étés trouvés :")
                for i, chemin_possible in enumerate(chemins): # affichage des chemins trouvés
                    print(f" {colors['reverse']}{i}{colors['reset']} : {chemin_possible}") # affichage au format "0 : [CHEMIN]"
                index = input("Indiquez l'indice du fichier cible : ")
                if not index.isdigit(): # on demande à nouveau le chemin si la valeur indiquée n'est pas un nombre
                    print("L'indice indiqué n'est pas un nombre.")
                    continue
                index = int(index)
                if index < 0 or index >= len(chemins): # on demande à nouveau le chemin si l'indice est invalide
                    print("L'indice indiqué est invalide.")
                    continue
                chemin = chemins[index] # on récupère le chemin indiqué
                selected = True # on sort de la boucle
            print(f"{colors['fg']['green']}Le fichier {chemin} a été selectionné.{colors['reset']}") # on affiche le chemin du fichier
        
        # on a un seul fichier, on le retourne
        else:
            chemin = chemins[0] # on récupère le fichier
            print(f"{colors['fg']['green']}Le fichier {chemin} a bien été trouvé !{colors['reset']}")

    return chemin

def ask_date(message: str = "Entrez la date (laissez vide pour ne pas utiliser de date): ") -> datetime.datetime:
    raw_date = input(message + colors['fg']['yellow'])
    print(colors['reset'], end="")
    if raw_date == "":
        return None # on désactive la date si on en rentre rien
    if raw_date.isdigit(): # Si la date est un entier, on considère qu'il s'agit d'un timestamp Unix
        return datetime.datetime.fromtimestamp(int(raw_date))
    else:
        # On essai différents formats de date courants
        try:
            return datetime.datetime.fromisoformat(
                raw_date,
            )
        except ValueError:
            pass
        try:
            return datetime.datetime.strptime(
                raw_date,
                "%d/%m/%Y",
            )
        except ValueError:
            pass
        try:
            return datetime.datetime.strptime(
                raw_date,
                "%d-%m-%Y",
            )
        except ValueError:
            pass
        # TODO mettre plus de formats de dates et heure
        print(f"{colors['fg']['red']}Je n'ai pas comprit la date {raw_date} !{colors['reset']} Réessaies avec un autre format !") # on affiche un message d'erreur
        return ask_date(message) # on rappelle la fonction pour redemander à l'utilisateur la date

# Partie de traitement des données
def filter_check(
    row: List[Any],
    reg: Optional[str],
    date: Optional[Tuple[Union[datetime.datetime, None]]],
    keep_ages: bool = False,
) -> bool:
    """Indique si la ligne doit être filtrée ou non
    Le filtre garde uniquement la classe d'âge 0.

    :param row: La ligne à filtrer
    :type row: List[Any]
    :param reg: La région du filtre (si None, pas de filtre de région)
    :type reg: Optional[str]
    :param date: Le filtre de date (si None, pas de filtre de date)
    :type date: Optional[Tuple[Union[datetime.datetime, None]]]
    :return: True si la ligne doit être gardée, False sinon
    :rtype: bool
    """
    check = True
    if not keep_ages:
        check = check and row[1] == "0"
    
    if reg is not None: # on vérifie qu'il faut appliquer le filtre de région
        check = check and row[0] == reg
    
    if date is not None: # on vérifie qu'il faut appliquer le filtre de date
        row_date = datetime.datetime.fromisoformat(row[2])
        # récupération de la date sous forme d'un objet facilement utilisable en python
        date_check = True
        if date[0] is not None: # on ignore le cas où on a pas de limite minimum
            date_check = date_check and date[0] <= row_date
        date_check = date_check and date[1] >= row_date
        check = check and date_check
    
    return check

def apply_filter(
    data: List[List[Any]],
    reg: Optional[str],
    date: Optional[Tuple[Union[datetime.datetime, None]]],
    keep_ages: bool = False,
) -> List[List[Any]]:
    """Applique les filtres indiqués sur la base de données

    :param data: La base de données sur lesquelles appliquer les filtres
    :type data: List[List[Any]]
    :param reg: La région du filtre (si None, pas de filtre de région)
    :type reg: Optional[str]
    :param date: Le filtre de date (si None pas de filtre de date)
    :type date: Optional[Tuple[Union[datetime.datetime, None]]]
    :return: La base de données avec les filtres appliqués
    :rtype: List[List[Any]]
    """
    return selection(
        data,
        lambda row: filter_check(row, reg, date, keep_ages),
    )

def convert_database(
    data: List[List[Any]],
) -> List[List[Any]]:
    for row in data:
        if not isinstance(row[2], datetime.datetime):
            row[2] = datetime.datetime.fromisoformat(row[2])
    
    return data

# Partie de traitement des images
def export_plot_to_image() -> Image.Image:
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')

    img = Image.open(buffer)
    
    return img

def get_diagram_1(database: List[List[Any]]) -> Image.Image:
    une_dose = [
        float(ligne[24]) for ligne in database
    ]
    complet = [
        float(ligne[25]) for ligne in database
    ]
    rappel = [
        float(ligne[26]) for ligne in database
    ]
    x_axis = [
        ligne[2] for ligne in database
    ]
    plt.figure()
    plt.fill_between(x_axis, une_dose, 0, )
    plt.fill_between(x_axis, complet, 0)
    plt.fill_between(x_axis, rappel, 0)

    return export_plot_to_image()

def get_diagram_2(database: List[List[Any]]) -> Image.Image:
    last_data = database[-1]
    
    axes = ['Hommes', 'Femmes', 'Couverture totale']
    values = [float(last_data[10]), float(last_data[19]), float(last_data[28])]

    plt.figure()
    plt.bar(axes, values)
    plt.axis([-1, 3, 0, 100])

    return export_plot_to_image()

def get_diagram_3(database: List[List[Any]]) -> Image.Image:
    plt.figure()
    for code, label in AGES:
        data = [line for line in database if line[1]==code]
        couv = [float(line[28]) for line in data]
        dates = [line[2] for line in data]
        plt.plot(dates, couv)
    
    return export_plot_to_image()

def get_diagram_4(database: List[List[Any]]) -> Image.Image:
    plt.figure()
    line = database[-1] # on prend en compte le fait que la bdd est triée par ordre croissant de date
    dose_3 = float(line[29])
    dose_2 = float(line[28]) - dose_3
    dose_1 = float(line[27]) - (dose_2 + dose_3)
    data = [dose_1, dose_2, dose_3, 100-float(line[27])]
    plt.pie(
        data
    )
    return export_plot_to_image()

def get_diagram_5(database: List[List[Any]]) -> Image.Image:
    plt.figure()
    dose_1, dose_2, dose_3, other = [], [], [], []
    regions = []
    for code, label in AGES:
        data = [line for line in database if line[1]==code][-1]
        # on récupère les informations les plus récentes, en
        # assumant que les données sont triées par date croissante
        age_dose_3 = float(data[29])
        age_dose_2 = float(data[28]) - age_dose_3
        age_dose_1 = float(data[27]) - (age_dose_2 + age_dose_3)
        dose_1.append(age_dose_1)
        dose_2.append(age_dose_2)
        dose_3.append(age_dose_3)
        other.append(100.0)
        regions.append(label)
    
    plt.barh(regions, other)
    plt.barh(regions, dose_3)
    plt.barh(regions, dose_2)
    plt.barh(regions, dose_1)

    return export_plot_to_image()

def get_diagram_6(database: List[List[Any]]) -> Image.Image:
    plt.figure()
    regions = []
    for code, nom in REGIONS.items():
        reg_data = [data for data in database if data[0] == code]
        # on récupère les informations les plus récentes, en assumant
        # que les données sont triées par date croissante et limitée
        # à la date recherchée
        regions.append(
            [code, float(reg_data[-1][28]), nom]
        )
    
    regions.sort(key=lambda reg: reg[1], reverse=True)
    regions = regions[:5] # on récupère les 5 régions qui ont la plus haute couverture
    
    plt.axis([-1, 5, 0, 100])

    for code, couv, nom in regions:
        plt.bar(nom, couv)
    
    return export_plot_to_image()

# Partie logique du script
if __name__ == "__main__": # on permet à un autre programme d'utiliser le code
    database_path = ask_file()
    
    print("Chargement du fichier...", end=" ", flush=True)
    # end permet de ne pas mettre de retour à la ligne
    # flush permet d'afficher le texte immédiatement sans attendre le retour à la ligne
    database = load_file(database_path)
    print(f"{colors['fg']['green']}Fait{colors['reset']}")

    reg = None
    while reg is None:
        reg = input(f"Indiquez un filtre de région : {colors['fg']['yellow']}") # on demande le code de la région
        print(colors['reset'], end="")
        if reg == "":
            reg = None
        else:
            print("Vérification du filtre...", end=" ", flush=True)
            if [reg] not in projection(database, (0,)): # on valide le code de la région pour éviter de n'avoir aucunes données
                print(f"{colors['fg']['red']}Filtre invalide{colors['reset']}")
                reg = None
            else:
                print(f"{colors['fg']['green']}Filtre valide{colors['reset']}")
    
    print("La plus grande date indiquée sera la date utilisée pour les graphiques instantannés.")
    print("Si aucune limite n'est spécifiée, les données les plus récentes sont utilisées.")
    print("Dans le filtre de dates, les deux extrémités sont comprises.")
    date1 = ask_date("Entrez une des dates limites (laissez vide pour désactiver les limites): ")
    if date1 is not None:
        date2 = ask_date("Entrez la deuxième date limite (laissez vide pour prendre toutes les dates avant le) : ")
        if date2 is None:
            date = (None, date1)
        else:
            if date1 == date2: # sélection d'une seul jour
                print("Impossible d'afficher un graphique pour une journée.")
                print("Toutes les valeurs seront affichées")
                date = None
            elif date1 > date2: # on peut comparer les dates
                date = (date2, date1)
            else:
                date = (date1, date2)
    else:
        date = None
    # date est soit None (pas de filtre de date), soit un tuple contenant la
    # plus petite date (ou None si pas de limite inférieure) et la plus grande
    # date du filtre
    
    print("Application du filtre et conversion des données...", end=" ", flush=True)
    not_filtered_database = database
    database_fall = apply_filter(database, reg, date) # on applique le filtre (suppression des régions non sélectionnées et suppression des dates n'étant pas dans l'interval)
    database_fage = apply_filter(database, reg, date, True) # on applique le filtre en gardant toutes les classes d'âge
    database_freg = apply_filter(database, None, date) # on applique le filtre en gardant toutes les régions
    # conversion des dates en objets datetime.datetime en utilisant le format ISO
    database_fall = convert_database(database_fall)
    database_fage = convert_database(database_fage)
    database_freg = convert_database(database_freg)
    print(f"{colors['fg']['green']}Fait{colors['reset']}")

    print("Génération des images...", end=" ", flush=True)
    diagram1 = get_diagram_1(database_fall)
    diagram2 = get_diagram_2(database_fall)
    diagram3 = get_diagram_3(database_fage)
    diagram4 = get_diagram_4(database_fall)
    diagram5 = get_diagram_5(database_fage)
    diagram6 = get_diagram_6(database_freg)
    print(f"{colors['fg']['green']}Fait{colors['reset']}")

    print("Génération de l'image finale...", end=" ", flush=True)
    print(f"{colors['fg']['green']}Fait{colors['reset']}")

    # exportation des images dans un dossier temporaire
    for i, diagram in enumerate([
        diagram1,
        diagram2,
        diagram3,
        diagram4,
        diagram5,
        diagram6,
    ]):
        diagram.save(f"output/diagram_{i+1}.png")
