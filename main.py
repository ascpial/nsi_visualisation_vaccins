# Importation des utilitaires n'étant pas en rapports avec la logique du code
from typing import Any, Callable, List, Optional, Tuple, Union

# Importation du module de lecture de base de données
import os
import csv

# Importation du module utilisé pour la détecection automatique du fichier
import glob

# Importation des module nécessaire à la gestion du temps
import datetime
import time

import io # nécessaire pour la conversion de l'image plot en image PIL

# On indique les modules à importer si une des importations échoue
try:
    # Importation des modules nécessaires au traitement de l'image
    import matplotlib.pyplot as plt
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    print("Vous devez installer les modules matplotlib et pillow pour utiliser ce programme")
    print("Pour installer les modules, utilisez la commande suivante:")
    print("pip install pillow matplotlib")

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
    ('80', "80 +"),
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

REG = 0
AGE = 1
JOUR = 2
CUMULE_DOSE1_E = 31
CUMULE_COMPLET_E = 32
CUMULE_RAPPEL_E = 33
CUMULE_2_RAPPEL_E = 34

COUV_DOSE1_E = 35
COUV_COMPLET_E = 36
COUV_RAPPEL_E = 37
COUV_2_RAPPEL_E = 38

COUV_COMPLET_H = 12
COUV_COMPLET_F = 24

# Cette constante permet de gérer l'affichage en couleur
COLORS = {
    'reset':'\033[0m',
    'bold':'\033[01m',
    'disable':'\033[02m',
    'underline':'\033[04m',
    'reverse':'\033[07m',
    'strikethrough':'\033[09m',
    'invisible':'\033[08m',
    'fg': {
        'black':'\033[30m',
        'red':'\033[31m',
        'green':'\033[32m',
        'orange':'\033[33m',
        'blue':'\033[34m',
        'purple':'\033[35m',
        'cyan':'\033[36m',
        'lightgrey':'\033[37m',
        'darkgrey':'\033[90m',
        'lightred':'\033[91m',
        'lightgreen':'\033[92m',
        'yellow':'\033[93m',
        'lightblue':'\033[94m',
        'pink':'\033[95m',
        'lightcyan':'\033[96m',
    },
    'bg': {
        'black':'\033[40m',
        'red':'\033[41m',
        'green':'\033[42m',
        'orange':'\033[43m',
        'blue':'\033[44m',
        'purple':'\033[45m',
        'cyan':'\033[46m',
        'lightgrey':'\033[47m',
    }
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
        f"Chemin du fichier à lire (laisser vide pour une détection automatique){' (saississez d pour le téléchargement automatique)' if DOWNLOAD_SUPPORT else ''} : {COLORS['fg']['yellow']}"
    )
    print(COLORS['reset'], end="")

    if chemin == 'd' and DOWNLOAD_SUPPORT:
        chemin = start_download()
    
    elif chemin == "": # on tente une détection automatique
        chemins = glob.glob("./vacsi-s-a-reg-*.csv")
        
        # on n'a pas trouvé de fichier
        if len(chemins) == 0:
            print(f"{COLORS['fg']['red']}Aucun fichier correspondant n'a été trouvé dans le répertoire actuel.{COLORS['reset']}")
            print(f"{COLORS['underline']}Merci de spécifier le chemin du fichier.{COLORS['reset']}")
            return ask_file() # on redemande le fichier
        
        # si il y a plusieurs fichiers qui correspondent
        elif len(chemins) > 1:
            selected = False # la boucle sera exécutée tant que selected vaut False
            while not selected:
                print("Les fichiers suivants ont étés trouvés :")
                for i, chemin_possible in enumerate(chemins): # affichage des chemins trouvés
                    print(f" {COLORS['reverse']}{i}{COLORS['reset']} : {chemin_possible}") # affichage au format "0 : [CHEMIN]"
                index = input(f"Indiquez l'indice du fichier cible : {COLORS['fg']['yellow']}")
                print(COLORS['reset'], end="")
                if not index.isdigit(): # on demande à nouveau le chemin si la valeur indiquée n'est pas un nombre
                    print("L'indice indiqué n'est pas un nombre.")
                    continue
                index = int(index)
                if index < 0 or index >= len(chemins): # on demande à nouveau le chemin si l'indice est invalide
                    print("L'indice indiqué est invalide.")
                    continue
                chemin = chemins[index] # on récupère le chemin indiqué
                selected = True # on sort de la boucle
            print(f"{COLORS['fg']['green']}Le fichier {chemin} a été selectionné.{COLORS['reset']}") # on affiche le chemin du fichier
        
        # on a un seul fichier, on le retourne
        else:
            chemin = chemins[0] # on récupère le fichier
            print(f"{COLORS['fg']['green']}Le fichier {chemin} a bien été trouvé !{COLORS['reset']}")

    return chemin

def ask_date(message: str = "Entrez la date (laissez vide pour ne pas utiliser de date): ") -> datetime.datetime:
    """Demande à l'utilisateur la date à utiliser pour la sélection.

    :param message: Le message à afficher au moment de demander la
    date, par défaut :
    "Entrez la date (laissez vide pour ne pas utiliser de date): "
    :type message: str, optional
    :return: La date indiquée par l'utilisateur
    :rtype: datetime.datetime
    """
    raw_date = input(message + COLORS['fg']['yellow'])
    print(COLORS['reset'], end="")
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
        print(f"{COLORS['fg']['red']}Je n'ai pas comprit la date {raw_date} !{COLORS['reset']} Réessaies avec un autre format !") # on affiche un message d'erreur
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
        check = check and row[AGE] == "0"
    
    if reg is not None: # on vérifie qu'il faut appliquer le filtre de région
        check = check and row[REG] == reg
    
    if date is not None: # on vérifie qu'il faut appliquer le filtre de date
        row_date = datetime.datetime.fromisoformat(row[2])
        # récupération de la date sous forme d'un objet facilement utilisable en python
        date_check = True
        # on vérifie que la date est bien comprise entre les limites
        if date[REG] is not None: # on ignore le cas où on a pas de limite minimum
            date_check = date_check and date[REG] <= row_date
        date_check = date_check and date[AGE] >= row_date
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
    # on applique le filtre en utilisant la fonction filter_check
    return selection(
        data,
        lambda row: filter_check(row, reg, date, keep_ages),
    )

def convert_database(
    data: List[List[Any]],
) -> List[List[Any]]:
    """Convertit certaines colonnes de la database vers des types plus appropriés

    :param data: La base de données à convertir
    :type data: List[List[Any]]
    :return: La base de données convertie
    :rtype: List[List[Any]]
    """
    for row in data:
        # on convertit la date en objet datetime.datetime si nécessaire
        if not isinstance(row[JOUR], datetime.datetime):
            row[JOUR] = datetime.datetime.fromisoformat(row[2])
    
    return data

# Partie de traitement des images
def export_plot_to_image(fig=None) -> Image.Image:
    """Permet d'exporter le graphique matplotlib en image

    :param fig: La figure matplotlib à convertir.
    Si la figure n'est pas spécifiée, alors la figure courante est utilisée, par défaut à None
    :type fig: pyplot.subplots()[1], optional
    :return: L'image de la figure
    :rtype: Image.Image
    """
    # puisqu'on ne peut enregistrer une image que dans un fichier, on
    # crée un fichier temporaire stocké dans la mémoire
    buffer = io.BytesIO()

    # si aucune figure n'est spécifiée, on utilise la figure courante
    if fig is None:
        plt.savefig(buffer, format='png')
    else:
        fig.savefig(buffer, format='png')

    # on créé un image à partir du fichier temporaire
    img = Image.open(buffer)
    
    return img

def get_diagram_1(database: List[List[Any]]) -> Image.Image:
    """Retourne le prmier diagramme. Il affiche le nombre cumulé de
    personnes vaccinées dans la région indiquée au cour du temps.

    :param database: Las base de données d'où proviennent les données.
    Elle doit être convertie avec la fonction convert_database(),
    et doit ne contenir que les lignes de la région indiquée.
    :type database: List[List[Any]]
    :return: L'image correspondant au graphique
    :rtype: Image.Image
    """
    # on récupère les données correspondant aux différents stades de
    # vaccination
    une_dose = [
        float(ligne[CUMULE_DOSE1_E]) for ligne in database
    ]
    complet = [
        float(ligne[CUMULE_COMPLET_E]) for ligne in database
    ]
    rappel = [
        float(ligne[CUMULE_RAPPEL_E]) for ligne in database
    ]
    rappel_2 = [
        float(ligne[CUMULE_2_RAPPEL_E]) for ligne in database
    ]
    x_axis = [
        ligne[JOUR] for ligne in database
    ]
    # on créé le graphique
    fig, ax = plt.subplots()
    ax.set_title("Nombre cumulé de personnes vaccinées")
    # on indique les axes
    ax.set_ylabel("Nombre de personnes vaccinées")
    # on tourne les valeurs de l'axe X de 30°
    plt.xticks(rotation=30, ha="right")
    
    # on trace les courbes
    ax.fill_between(x_axis, une_dose, 0, label="Une dose (partiel)", color="tab:blue")
    ax.fill_between(x_axis, complet, 0, label="Deux doses (complet)", color="tab:orange")
    ax.fill_between(x_axis, rappel, 0, label="Trois doses (rappel)", color="tab:green")
    ax.fill_between(x_axis, rappel_2, 0, label="Quatre doses (rappel 2)", color="tab:olive")

    # on indique l'emplacement de la légende
    ax.legend(loc='upper left')
    
    return export_plot_to_image(fig)

def get_diagram_2(database: List[List[Any]]) -> Image.Image:
    """Retourne le second diagramme. Il affiche l'état de la
    couverture vaccinale en fonction du sexe dans la région indiquée.

    :param database: La base de données d'où proviennent les données.
    Elle ne doit contenir que les données de la région indiquée.
    :type database: List[List[Any]]
    :return: L'image correspondant au graphique
    :rtype: Image.Image
    """
    # on récupère les données du dernier jour (en assumant que les
    # données sont triés par date)
    last_data = database[-1]
    
    # on indique les étiquettes
    axes = ['Hommes', 'Femmes', 'Couverture totale']
    # on récupère les valeurs
    values = [
        float(last_data[COUV_COMPLET_H]),
        float(last_data[COUV_COMPLET_F]),
        float(last_data[COUV_COMPLET_E]),
    ]

    # on créé le graphique
    fig, ax = plt.subplots()
    # on indique le titre
    ax.set_title(f"Couverture vaccinale")
    # on indique les axes
    ax.set_ylabel("Couverture vaccinale (en %)")

    # on affiche le graphique
    ax.bar(axes, values, label="Couverture vaccinale", color=["tab:red", "tab:green", "tab:grey"])

    # on paramètre les axes pour une meilleur lisibilité
    ax.axis([-1, 3, 0, 100])

    return export_plot_to_image(fig)

def get_diagram_3(database: List[List[Any]]) -> Image.Image:
    """Retourne le troisième diagramme. Il affiche l'état de la
    couverture vaccinale en fonction de la classe d'âge dans la
    région indiquée.

    :param database: La base de données d'où proviennent les données.
    Elle doit être convertie avec la fonction convert_database(),
    et ne doit contenir que les lignes de la région indiquée, tout en
    conservant les données de la classe d'âge.
    :type database: List[List[Any]]
    :return: L'image correspondant au graphique
    :rtype: Image.Image
    """
    # on créé le graphique
    fig, ax = plt.subplots()
    # on indique un titre
    ax.set_title("Évolution de la couverture vaccinale")
    # on indique les axes
    ax.set_ylabel("Pourcentage de population vaccinée")
    # on tourne les valeurs de l'axe X de 30°
    plt.xticks(rotation=30, ha="right")
    
    # on récupère une liste de 14 couleurs
    colors = plt.cm.brg([
        0.,
        0.07692308,
        0.15384615,
        0.23076923,
        0.30769231,
        0.38461538,
        0.46153846,
        0.53846154,
        0.61538462,
        0.69230769,
        0.76923077,
        0.84615385,
        0.92307692,
        1.
    ])

    for i, (code, label) in enumerate(AGES): # pour chaque classe d'âges
        # on récupère toutes les données de la classe d'âges
        data = [line for line in database if line[1]==code]
        # on récupère les valeurs de la couverture vaccinale
        couv = [float(line[COUV_COMPLET_E]) for line in data]
        # on récupère les dates correspondantes aux valeurs
        dates = [line[2] for line in data]
        # on affiche le graphique
        ax.plot(dates, couv, label=label, color=colors[i])
    
    # on indique l'emplacement de la légende
    ax.legend(loc='upper left', fontsize=7)
    
    return export_plot_to_image(fig)

def get_diagram_4(database: List[List[Any]]) -> Image.Image:
    """Retourne le quatrième diagramme. Il affiche l'état de la
    vaccination dans un diagrame camembert dans la région indiquée.

    :param database: La base de données d'où proviennent les données.
    Elle ne doit contenir que les informations de la région indiquée.
    :type database: List[List[Any]]
    :return: L'image correspondant au graphique
    :rtype: Image.Image
    """
    # on créé le graphique
    fig, ax = plt.subplots()
    # on indique le titre
    ax.set_title(f"État de la vaccination")

    # on récupère les données en prenant en compte que les données sont triées par date
    line = database[-1]
    # on récupère les valeurs de la couverture vaccinale
    dose_4 = float(line[COUV_2_RAPPEL_E])
    dose_3 = float(line[COUV_RAPPEL_E]) - dose_4
    dose_2 = float(line[COUV_COMPLET_E]) - dose_3 - dose_4
    dose_1 = float(line[COUV_DOSE1_E]) - dose_2 - dose_3 - dose_4
    data = [
        100-float(line[COUV_DOSE1_E]),
        dose_1, dose_2, dose_3, dose_4,
    ]

    # on créé le diagramme camembert
    ax.pie(
        data,
        colors=["tab:red", "tab:blue", "tab:orange", "tab:green", "tab:olive"],
        # on spécifie la mise en forme des labels
        textprops={'size': 'large', 'fontweight': 'bold', 'color': 'white'},
        autopct = lambda value: f"{value:.1f}%",
    )

    # on affiche le graphique
    ax.legend(
        labels=["Pas vacciné", "Une dose (partiel)", "Deux doses (complet)", "Trois doses (rappel)", "Quatre doses (rappel 2)"],
        loc="lower left",
        bbox_to_anchor=(-0.3, 0.)
    )

    return export_plot_to_image(fig)

def get_diagram_5(database: List[List[Any]]) -> Image.Image:
    """Retourne le diagramme cinq. Il affiche la répartition de la
    vaccination en fonction de la classe d'âge dans la région
    indiquée.

    :param database: La base de données d'où proviennent les données.
    Elle ne doit contenir que les informations de la région indiquée,
    et contenir les informations de la classe d'âge.
    :type database: List[List[Any]]
    :return: L'image correspondant au graphique
    :rtype: Image.Image
    """
    # on créé le graphique
    fig, ax = plt.subplots()
    # on indique le titre
    ax.set_title("Répartition des vaccinations sur les classes d'âges")
    # on indique les axes
    ax.set_ylabel("Classe d'âge")
    ax.set_xlabel("Population vaccinée (en %)")

    # on récupère les données par dose
    dose_4, dose_1, dose_2, dose_3, non_vaccine = [], [], [], [], []
    classe_age = []
    for code, label in AGES: # pour chaque classe d'âges
        data = [line for line in database if line[1]==code][-1]
        # on récupère les informations les plus récentes, en
        # assumant que les données sont triées par date croissante
        age_dose_4 = float(data[COUV_2_RAPPEL_E])
        age_dose_3 = float(data[COUV_RAPPEL_E]) - age_dose_4
        age_dose_2 = float(data[COUV_COMPLET_E]) - age_dose_3 - age_dose_4
        age_dose_1 = float(data[COUV_DOSE1_E]) - age_dose_2 - age_dose_3 - age_dose_4
        age_0_dose = 100 - float(data[COUV_DOSE1_E])

        # on ajoute les valeurs aux listes
        non_vaccine.append(age_0_dose)
        dose_1.append(age_dose_1 + age_0_dose)
        dose_2.append(age_dose_2 + age_dose_1 + age_0_dose)
        dose_3.append(age_dose_3 + age_dose_2 + age_dose_1 + age_0_dose)
        dose_4.append(age_dose_4 + age_dose_3 + age_dose_2 + age_dose_1 + age_0_dose)
        # on ajoute la classe d'âge à la liste
        classe_age.append(label)
    
    ax.barh(classe_age, dose_3, color="tab:olive", label="Quatre doses (rappel 2)")
    ax.barh(classe_age, dose_3, color="tab:green", label="Trois doses (rappel)")
    ax.barh(classe_age, dose_2, color="tab:orange", label="Deux doses (complet)")
    ax.barh(classe_age, dose_1, color="tab:blue", label="Une dose (partiel)")
    ax.barh(classe_age, non_vaccine, color="tab:red", label="Pas vacciné")

    ax.legend(
        loc="upper right",
    )

    return export_plot_to_image(fig)

def get_diagram_6(database: List[List[Any]]) -> Image.Image:
    """Retourne le diagramme six. Il affiche les cinq régions où la
    couverture vaccinale est la plus élevée.

    :param database: La base de données d'où proviennent les données.
    Elle doit contenir les informations de toutes les régions.
    :type database: List[List[Any]]
    :return: L'image correspondant au graphique
    :rtype: Image.Image
    """
    # on créé le graphique
    fig, ax = plt.subplots()
    # on indique le titre
    ax.set_title("5 régions ayant la meilleure couverture vaccinale")
    # on indique les axes
    ax.set_ylabel("Couverture vaccinale (en %)")
    # on tourne les labels de l'axe x de 10°
    plt.xticks(rotation=10, ha="right")

    regions = []
    for code, nom in REGIONS.items(): # pour chaque région
        reg_data = [data for data in database if data[0] == code]
        # on récupère les informations les plus récentes, en assumant
        # que les données sont triées par date croissante et limitée
        # à la date recherchée
        regions.append(
            [code, float(reg_data[-1][COUV_COMPLET_E]), nom]
        )
    
    # on trie les régions par ordre décroissant
    regions.sort(key=lambda reg: reg[1], reverse=True)
    regions = regions[:5] # on récupère les 5 régions qui ont la plus haute couverture
    
    # on paramétre les axes pour une meilleur lisibilité
    ax.axis([-1, 5, 0, 100])

    # on affiche la barre pour chaque région
    for code, couv, nom in regions:
        ax.bar(nom, couv)
    
    return export_plot_to_image(fig)

# Partie logique du script
if __name__ == "__main__": # on permet à un autre programme d'utiliser le code
    database_path = ask_file()
    
    print("Chargement du fichier...", end=" ", flush=True)
    # end permet de ne pas mettre de retour à la ligne
    # flush permet d'afficher le texte immédiatement sans attendre le retour à la ligne
    database = load_file(database_path)
    print(f"{COLORS['fg']['green']}Fait{COLORS['reset']}")

    reg = None
    while reg is None:
        reg = input(f"Indiquez un filtre de région : {COLORS['fg']['yellow']}") # on demande le code de la région
        print(COLORS['reset'], end="")
        if reg == "":
            reg = None
        else:
            print("Vérification du filtre...", end=" ", flush=True)
            if [reg] not in projection(database, (0,)): # on valide le code de la région pour éviter de n'avoir aucunes données
                print(f"{COLORS['fg']['red']}Filtre invalide{COLORS['reset']}")
                reg = None
            else:
                print(f"{COLORS['fg']['green']}Filtre valide{COLORS['reset']}")
    
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
    print(f"{COLORS['fg']['green']}Fait{COLORS['reset']}")

    print("Génération des images...", end=" ", flush=True)
    diagram1 = get_diagram_1(database_fall)
    diagram2 = get_diagram_2(database_fall)
    diagram3 = get_diagram_3(database_fage)
    diagram4 = get_diagram_4(database_fall)
    diagram5 = get_diagram_5(database_fage)
    diagram6 = get_diagram_6(database_freg)
    print(f"{COLORS['fg']['green']}Fait{COLORS['reset']}")

    print("Génération de l'image finale...", end=" ", flush=True)
    
    # exportation des images dans une seule image
    diagram_size_x, diagram_size_y = diagram1.size

    # on crée une image vide avec un fond blanc
    img = Image.new("RGB", (diagram_size_x * 2, diagram_size_y * 3 + 64), "white")

    # on affiche "Données relatives à la COVID-19" en haut de l'image
    img_draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 60)
    img_draw.text((diagram_size_x, 24), "Données relatives à la COVID-19", (0, 0, 0), font=font, anchor="mm")

    # on colle les diagrammes dans l'image
    img.paste(diagram1, (0, 64))
    img.paste(diagram2, (diagram_size_x, 64))
    img.paste(diagram3, (0, diagram_size_y + 64))
    img.paste(diagram4, (diagram_size_x, diagram_size_y + 64))
    img.paste(diagram5, (0, diagram_size_y * 2 + 64))
    img.paste(diagram6, (diagram_size_x, diagram_size_y * 2 + 64))

    # on affiche en petit le nom de la région en dessous du titre
    # cette ligne de code risque de provoquer une erreur sur linux ou macos
    font = ImageFont.truetype("arial.ttf", 30)
    if date is not None:
        # on formate la date au format "jour/mois/année"
        formated_date = time.strftime("%d/%m/%Y", date[1].timetuple())
    else:
        last_date = database_fall[-1][JOUR]
        formated_date = time.strftime("%d/%m/%Y", last_date.timetuple())
    img_draw.text((diagram_size_x, 60), f"Région : {REGIONS[reg]}, date : {formated_date}", (0, 0, 0), font=font, anchor="mm")

    # si output.png existe alors on cherche un nom de fichier au format output_1.png, output_2.png, etc.
    # sinon on prend output.png
    if not os.path.exists("output.png"):
        output_path = "output.png"
    else:
        # on cherche le premier nom de fichier disponible
        i = 1
        while os.path.exists(f"output_{i}.png"):
            i += 1
        output_path = f"output_{i}.png"

    # on enregistre l'image dans le fichier output.png
    img.save(output_path)
    
    print(f"{COLORS['fg']['green']}Fait{COLORS['reset']}")