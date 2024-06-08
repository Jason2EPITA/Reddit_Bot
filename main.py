from solver import get_solver_input, parse_response, solver_csp
import praw
from utils import print_post_details
from config import username, client_id, client_secret, password, openai_api_key, gpt_key, llm

#Initialiser l'instance Reddit
reddit_instance = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent="test_bot",
    username=username,
    password=password
)

subreddit = reddit_instance.subreddit("testingground4bots")

print("Listenning on Reddit - testingground4bots for new posts...")
for post in subreddit.stream.submissions(skip_existing=True):
    if post.title.endswith("probleme"):
        print_post_details(post)
        problem_statement = post.selftext
        response = get_solver_input(problem_statement)
        variables, constraints = parse_response(response)
        solution = solver_csp(variables, constraints)
        final_prompt = f"La solution au problème est la suivante: {solution}. Reformulez la réponse pour qu'elle soit bien présentée."
        final_response = llm.invoke(final_prompt.format(solution=solution))
        post.reply(final_response)
        print("Répondu au post.")


#################################---POUR TESTER SANS REDDIT---######################################

# # Exemple de problème
# problem1 = "Nous devons répartir trois personnes, Alice, Bob et Charlie, dans trois salles (0, 1, et 2) de manière à ce que : Alice et Bob ne soient pas dans la même salle. La somme des indices des salles occupées par Alice, Bob et Charlie soit égale à 3."
# problem2 = "Vous devez vérifier s'il existe des entiers x et y tels que : x>5 𝑦<10 𝑥+𝑦=15"
# problem3 = """
# Remplissez la grille de Sudoku suivante :
# 5 3 _ | 7 _ _ | _ _ _
# 6 _ _ | 1 9 5 | _ _ _
# _ 9 8 | _ _ _ | 6 _ _

# ------|-------|------
# 8 _ _ | _ 6 _ | _ _ 3
# 4 _ _ | 8 _ 3 | _ _ 1
# 7 _ _ | _ 2 _ | _ _ 6

# ------|-------|------
# _ 6 _ | _ _ _ | 2 8 _
# _ _ _ | 4 1 9 | _ 5 _
# _ _ _ | _ 8 _ | _ 7 9
# """

# # Choisir le problème à résoudre
# problem_statement = problem1

# print("LE PROBLEME DE REDDIT : ", problem_statement)

# # Obtenir la réponse de ChatGPT
# response = get_solver_input(problem_statement)
# print("Réponse de ChatGPT :\n", response)

# # Parser la réponse pour obtenir les variables et contraintes
# variables, constraints = parse_response(response)
# print("\nVariables :", variables)
# print("Contraintes :", constraints)

# # Utiliser les variables et contraintes avec le solver
# solution = solver_csp(variables, constraints)

# print(solution)
