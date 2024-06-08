import datetime
import requests

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


# Fonction pour demander à Better GPT
def ask_bettergpt(question, gpt_key, gpt_url, model, preparation_prompt):
    headers = {
        "Authorization": f"Bearer {gpt_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": preparation_prompt  # Votre prompt personnalisé ici
            },
            {
                "role": "user",
                "content": question
            }
        ]
    }

    response = requests.post(gpt_url, json=data, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        answer = response_data["choices"][0]["message"]["content"]
        return answer
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None