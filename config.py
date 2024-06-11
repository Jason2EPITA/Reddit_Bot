import os
from dotenv import load_dotenv
from langchain_openai import OpenAI,ChatOpenAI  # Importer OpenAI de langchain_openai
import sys
import subprocess
import platform
from typing import Optional

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupérer la valeur des variables d'environnement
username = os.getenv("USERNAME")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
password = os.getenv("PASSWORD")
openai_api_key = os.getenv("OPENAI_API_KEY")
gpt_key = os.getenv("GPT_KEY")

# Configurer l'instance OpenAI de LangChain
llm = OpenAI(api_key=gpt_key)
llm2=ChatOpenAI(model="gpt-4o",temperature=0)

# Fonction pour obtenir le chemin du solveur Choco
def get_choco_solver_path() -> str:
    """
    Obtient le chemin du solveur Choco.

    Returns:
        str: Chemin du solveur Choco.
    """
    current_path: str = os.path.dirname(os.path.abspath(sys.argv[0]))

    while not os.path.exists(os.path.join(current_path, "solvers")):
        current_path = os.path.dirname(current_path)
        if current_path == os.path.dirname(current_path):
            raise FileNotFoundError("Unable to find the root directory of the project.")

    return os.path.join(current_path, "solvers", "choco-parsers-4.10.14-light.jar")

# Fonction pour installer le paquet GLPK
def install_glpk_package() -> None:
    """
    Installe le paquet GLPK selon le système d'exploitation.

    Raises:
        NotImplementedError: Si le système d'exploitation n'est pas pris en charge.
    """
    if platform.system() == "Darwin":
        # macOS: Installer le paquet glpk avec Homebrew
        print("Installation du paquet glpk avec Homebrew...")
        subprocess.run(["brew", "install", "glpk"])
    elif platform.system() == "Linux":
        # Linux: Vérifier si glpk-utils est déjà installé
        result = subprocess.run("dpkg -s glpk-utils", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("Le paquet glpk-utils est déjà installé.")
        else:
            # glpk-utils n'est pas installé, exécuter la commande sudo apt-get install glpk-utils
            print("Le paquet glpk-utils n'est pas installé. Exécution de la commande pour l'installer...")
            subprocess.run("sudo apt-get install glpk-utils", shell=True)
    else:
        raise NotImplementedError("Système d'exploitation non pris en charge.")
