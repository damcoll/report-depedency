import subprocess
import os
import argparse
import csv
import requests
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
import codecs
import re

# audit_url = f"https://registry.npmjs.org/-/npm/v1/security/advisories"
# audit_response = requests.get(audit_url)
# security_advisories = audit_response.json()
# print (security_advisories)

def exec_npm_audit(package_name, package_version):
    commande = f"npm audit --audit-level=moderate --package={package_name}/{package_version}"

    # Utilisez subprocess pour exécuter la commande
    try:
        resultat = subprocess.run(commande, shell=True, capture_output=True, text=True, check=True)
        sortie = resultat.stdout
        erreur = resultat.stderr
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {e}")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")



def exec_commande(chemin_projet, cmd):
    resultat = ""
    try:
        resultat = subprocess.run(cmd, shell=True, cwd=chemin_projet, capture_output=True, text=True, check=True)
    except Exception as e:
        resultat = e.stdout
    write_temp_file(resultat)

def write_temp_file(text_to_append):
    with open(file_name, "a") as file:
    # Append the text to the file
        file.write(text_to_append)

def comp_version(version, wanted) :
    compar = ""
    version = extract_version(version)
    wanted =  extract_version(wanted)
    majeur = 0
    mineur = 0
    patch = 0
    if str(version[0]).isnumeric() and str(wanted[0]).isnumeric():
        majeur = abs(int(wanted[0]) - int(version[0]))
    # if len (version) > 1 and str(version[1]).isnumeric() and str(wanted[1]).isnumeric():
    #     mineur = abs(int(wanted[1]) - int(version[1]))
    # else:
    #     return ""
    # if len (version) > 1 and str(version[2]).isnumeric() and str(wanted[2]).isnumeric():
    #     patch = abs(int(wanted[2]) - int(version[2]))

    # print(majeur)
    return majeur ##+ "." + str(mineur) + "." + str(patch)
 
def extract_version(version):
    version = version.replace('.',  ',')
    version_retour = []
    # reader = csv.reader(version, delimiter=",")
    text = ""
    for index, row in enumerate(version.split(',')):
        version_retour.append(row)
            
    return version_retour 

def get_date_package (version_actual, package_info) :
    try :
        return package_info["time"][version_actual]
    except :
        return datetime.min.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def notation_version(package_name, version_actual, package_info) :
    note = 0
    ##package_info["time"][last_version]
    # si la version a + de 1 version majeur / 2 et ++ == +1 / + 2
    # si la version actuel a + de 6 mois == + 1
    # si la  dernier version a + de 6 mois  = + 2 
    versions = list(package_info["time"].keys())
    last_version = versions[-1]
    version_actual = re.sub(r'[^a-zA-Z0-9.\s]', '', version_actual)

    dif = comp_version(version_actual, last_version)
    if dif == 1 :
        note+=1
    if dif > 1:
        note+=1
    if tchekup_dates(get_date_package(version_actual, package_info)):
        note+=1
    if tchekup_dates(package_info["time"][last_version]) :
        note += 2 

    return note


def check_package(package_name, version_value):
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url)
    if response.status_code == 200:
        package_info = response.json()
        versions = list(package_info["time"].keys())
        last_version = versions[-1]
        note = notation_version(package_name, version_value, package_info)
        return [package_name, re.sub(r'[^a-zA-Z0-9.\s]', '', version_value), package_info["time"][last_version], last_version,[note]]


def tchekup_dates(date):
    try :
        difference = abs( datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.now())
        return difference > timedelta(days=180) ## 6 mois 
    except:
        return True

# PATH
chemin_projet = "."
chemin_package_json = chemin_projet + "package.json"
chemin_pom_xml = chemin_projet + "pom.xml"

# COMMANDE

cmd_maven = "mvn versions:display-dependency-updates"
cmd_npm = "npm outdated"
cmd_test = "pwd"


# VARIABLE

file_name = ".temporarydependency"
maven_exist = False
npm_exist = False

# ARGUMENTS DU PROGRAMME

parser = argparse.ArgumentParser(description="Chemin du projets a analyser.")
parser.add_argument("--path", help="Chemin du dossier à traiter")
args = parser.parse_args()

if args.path:
    chemin_projet = args.path
    chemin_package_json = chemin_projet + "/package.json"
    chemin_package_json = chemin_package_json.replace("//", "/").replace("\n", "")
    chemin_pom_xml = chemin_projet + "/pom.xml"
    chemin_pom_xml = chemin_package_json.replace("//", "/").replace("\n", "")

# TEST EXISTANCE FICHIER
if os.path.exists(chemin_package_json):
    npm_exist = True

if os.path.exists(chemin_pom_xml):
    maven_exist = True

if os.path.exists(file_name):
    # Remove (delete) the file
    os.remove(file_name)

# EXECUTION DES COMMANDES

write_temp_file("")


with open(chemin_package_json, 'r') as file:
    # Charger le contenu du fichier JSON
    data = json.load(file)
    print(data['name'])

data_value_npm = []
for dependencies in data['dependencies']:
    data_value_npm.append([dependencies,  data['dependencies'][dependencies]])
for dependencies in data['devDependencies']:
    data_value_npm.append([dependencies,  data['devDependencies'][dependencies]])

data_value_npm_date = []

for package in data_value_npm :
    if package and package[0]:
        data_value_npm_date.append(check_package(package[0], package[1]))

warnning_package = []
for package in data_value_npm_date :
    if package and package[0] and package[1]:
        warnning_package.append(package)


html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid black;
        }
        th, td {
            padding: 10px;
            text-align: center;
        }
        th {
            background-color: #66cc66;
            color: #FFFFFF;
        }
        tr:nth-child(odd) {
            background-color: #e6ffe6;
        }
        tr:nth-child(even) {
            background-color: #ffdddd;
        }
    </style>
</head>
<body>
    <h1>Rapport d'obsolescence des dépendances """ + data['name'] + """ du """ + datetime.now().strftime("%B %Y") + """</h1>
    <table>
        <tr>
            <th>Nom de la dépendance</th>
            <th>Version actuelle</th>
            <th>Dernière version</th>
            <th>Note d'obsolescence (0 à jour)</th>
        </tr>
"""

# Ajouter les lignes de données dans le rapport
for dependency in warnning_package:
    html_content += f"""
        <tr>
            <td>{dependency[0]}</td>
            <td>{dependency[1]}</td>
            <td>{datetime.strptime(dependency[2], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%B %Y")} ({dependency[3]})</td>
            <td><b>{dependency[4][0]}</b></td>
        </tr>
    """

# Fermer la balise body et html
html_content += """
    </table>
</body>
</html>
"""

# Enregistrer le rapport HTML dans un fichier
with open("rapport_obsolescence.html", "w") as html_file:
    html_file.write(html_content)

print("Rapport HTML généré avec succès.")

