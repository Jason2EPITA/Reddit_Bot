import os
from dotenv import load_dotenv
from langchain_openai import OpenAI  # Importer OpenAI de langchain_openai

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
