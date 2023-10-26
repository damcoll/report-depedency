import subprocess
import os
import argparse
import csv
import requests
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
import codecs

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
    majeur = ""
    mineur = ""
    patch = ""
    if str(version[0]).isnumeric() and str(wanted[0]).isnumeric():
        majeur = abs(int(wanted[0]) - int(version[0]))
    if len (version) > 1 and str(version[1]).isnumeric() and str(wanted[1]).isnumeric():
        mineur = abs(int(wanted[1]) - int(version[1]))
    else:
        return ""
    if len (version) > 1 and str(version[2]).isnumeric() and str(wanted[2]).isnumeric():
        patch = abs(int(wanted[2]) - int(version[2]))

    # print(majeur)
    return str(majeur) + "." + str(mineur) + "." + str(patch)
 
def extract_version(version):
    version = version.replace('.',  ',')
    version_retour = []
    # reader = csv.reader(version, delimiter=",")
    text = ""
    for index, row in enumerate(version.split(',')):
        version_retour.append(row)
            
    return version_retour 

def check_package(package_name):
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url)
    if response.status_code == 200:
        package_info = response.json()
        versions = list(package_info["time"].keys())
        last_version = versions[-1]
        return [package_name, package_info["time"][last_version]]


def tchekup_dates(date):
    difference = abs( datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ") - datetime.now())
    return difference > timedelta(days=180)

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
    # print(data['version'])
    # print(data['devDependencies'])

data_value_npm = []
for dependencies in data['dependencies']:
    data_value_npm.append([dependencies,  data['dependencies'][dependencies]])
for dependencies in data['devDependencies']:
    data_value_npm.append([dependencies,  data['devDependencies'][dependencies]])

data_value_npm_date = []

for package in data_value_npm :
    if package and package[0]:
        data_value_npm_date.append(check_package(package[0]))
warnning_package = []
for package in data_value_npm_date :
    if package and package[0] and package[1]:
        if tchekup_dates(package[1]) :
            warnning_package.append(package)



# Spécifiez le chemin vers le fichier HTML
fichier_html = ".example.html"

# Ouvrez le fichier HTML
with open(fichier_html, "r", encoding="utf-8") as file:
    html_content = file.read()

# Analysez le contenu HTML avec BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Trouvez la div avec un identifiant spécifique
div_with_id = soup.find("ul", id="add")

for w in warnning_package:
    if div_with_id:
        # Créez un nouvel élément <p>
        new_paragraph = soup.new_tag("li")
        
        # Ajoutez du texte au paragraphe
        new_paragraph.string = w[0] +  "-" + w[1]

        # Ajoutez le paragraphe à l'intérieur de la div
        div_with_id.append(new_paragraph)

        # Enregistrez les modifications dans un nouveau fichier ou écrivez-les dans le fichier d'origine
        with open("rapport.html", "w", encoding="utf-8") as new_file:
            new_file.write(soup.prettify())  # Écrit le contenu formaté dans le nouveau fichier

# if npm_exist:
#     exec_commande(chemin_projet, cmd_npm)
#     parsed_data = []
#     data_value_npm = []
#     with open(file_name, "r", newline="") as file:
#         reader = csv.reader(file, delimiter="\t")
#         for index, row in enumerate(reader):
#             parsed_data.append(row)
#             reader2 = csv.reader(row, delimiter=" ")
#             tab_temp = []
#             for index, row2 in enumerate(reader2):
#                 for index, val in enumerate(row2):
#                     if (len(val) > 1):
#                         tab_temp.append(val)
#             data_value_npm.append([tab_temp[0], tab_temp[1], tab_temp[3], comp_version(tab_temp[1], tab_temp[3])]);           

# if os.path.exists(file_name):
#     # Remove (delete) the file
#     os.remove(file_name)

# file_path = "output.csv"

# # data_value_npm



# # Write the table to the CSV file
# with open(file_path, "w", newline="") as file:
#     writer = csv.writer(file)
#     writer.writerows(data_value_npm)

# # if maven_exist:
# #     exec_commande(chemin_projet, cmd_maven)
# #     #TODO
