import os
from dotenv import load_dotenv
import praw
from datetime import datetime
import requests
from utils import print_post_details, ask_bettergpt
# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupérer la valeur de la variable d'environnement
username = os.getenv("USERNAME")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
password = os.getenv("PASSWORD")


gpt_key = os.getenv("GPT_KEY")
gpt_url = os.getenv("GPT_URL")

reddit_instance = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent="test_bot",
    username=username,
    password=password
)

# print(reddit_instance.user.me())

# Récupérer les IDs des commentaires auxquels le bot a déjà répondu
replied_comments = set()
for comment in reddit_instance.redditor(username).comments.new(limit=None):
    replied_comments.add(comment.parent_id)

# Définir le chemin du fichier pour stocker les identifiants des posts auxquels vous avez déjà répondu
replied_posts_file = "replied_comments.txt"

# Charger les identifiants des posts déjà répondu depuis le fichier
replied_posts = set()
with open(replied_posts_file, "r") as file:
    for line in file:
        replied_posts.add(line.strip())

# Écouter en permanence les nouveaux posts dans la communauté r/all
communitie = "testingground4bots" # Écouter les nouveaux posts dans la communauté r/all (all c toute les communautés)
subreddit = reddit_instance.subreddit(communitie)
for post in subreddit.stream.submissions(skip_existing=True):
    # print_post_details(post)
# MATHS TEST
    if post.title.endswith("probleme") and post.id not in replied_posts:
        prompt= "Tu es un génie en mathématiques, mais aussi tu aime faire des blagues. Tu ne dois jamais mentionner openai ou autre chose qui montre  a qui tu appartenanait, la seule chose que tu peux dire c'est que tu es un assistant creer par l'equipe REDBOTJASONLEBG. Repond a la question de facon simple et ajoute une blague de maths a la fin."
        question = post.selftext
        response = ask_bettergpt(question, gpt_key, gpt_url, "gpt-4o",prompt)
        print(f"LA REPONSE : {response}")        
        
        post.reply(response)
        
        print("Répondu au post:", post.title)
        print("*************")
        
        replied_posts.add(post.id)

# LMAO TEST 
    if post.selftext.endswith("quoi ?") and post.id not in replied_posts:
        # Répondre au post lui-même
        post.reply("quoicoubeh au post!")
        print("Répondu au post:", post.title)
        print("*************")

        # Ajouter l'identifiant du post à l'ensemble des posts déjà répondu
        replied_posts.add(post.id)

# Enregistrer les identifiants des posts auxquels vous avez répondu dans le fichier
with open(replied_posts_file, "w") as file:
    for post_id in replied_posts:
        file.write(post_id + "\n")
