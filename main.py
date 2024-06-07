import os
from dotenv import load_dotenv
import praw
from datetime import datetime
# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupérer la valeur de la variable d'environnement
username = os.getenv("USERNAME")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
password = os.getenv("PASSWORD")

reddit_instance = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent="test_bot",
    username=username,
    password=password
)

# print(reddit_instance.user.me())
# Récupérer les 5 derniers posts dans la communauté r/testingground4bots
subreddit = reddit_instance.subreddit("testingground4bots")
recent_posts = subreddit.new(limit=5)

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

# Parcourir les 5 derniers posts
for post in recent_posts:
    # Vérifier si vous avez déjà répondu à ce post
    if post.id in replied_posts:
        continue

    post.comments.replace_more(limit=None)
    # print("Titre du post:", post.title)
    # print("Texte du post:", post.selftext)  # Afficher le texte du post
    # print("URL du post:", post.url)          # Afficher l'URL du post
    if post.selftext.endswith("quoi"):
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


# Fonction pour afficher les détails du post
def print_post_details(post):
    author = post.author.name if post.author else "N/A"
    created_utc = datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
    print("*****Nouveau post détecté*****")
    # print(f"** Nouveau post détecté **")
    print(f"Titre: {post.title}")
    print(f"Auteur: {author}")
    print(f"Date de création (UTC): {created_utc}")
    # print(f"URL: {post.url}")
    print(f"Texte du post: {post.selftext}")
    print("\n")

# Écouter en permanence les nouveaux posts dans la communauté r/all
communitie = "all" # Écouter les nouveaux posts dans la communauté r/all (all c toute les communautés)
subreddit = reddit_instance.subreddit(communitie)
for post in subreddit.stream.submissions(skip_existing=True):
    print_post_details(post)