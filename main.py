from solver import get_solver_input, parse_response_probleme_csp, solver_csp, parse_sudoku_grid, solver_sudoku_with_pulp, get_solver_sudoku_input
import praw
from solver import get_planning_sat_input, parse_json_response, solve_sat, afficher_solution
from utils import print_post_details
from config import username, client_id, client_secret, password, openai_api_key, gpt_key, llm, install_glpk_package,llm2
from timeit import default_timer as timer
import numpy as np
import re
# install_glpk_package() # Installer le paquet GLPK

# Initialiser l'instance Reddit
reddit_instance = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent="test_bot",
    username=username,
    password=password
)

# Récupérer le subreddit
subreddit_title = "testingground4bots"
subreddit = reddit_instance.subreddit(subreddit_title)
print(f'Listenning on Reddit - {subreddit_title} for new posts...')

# Définir la fonction pour résoudre les problèmes CSP
def solve_csp_reddit(problem_statement: str) -> str:
    response = get_solver_input(problem_statement)
    variables, constraints = parse_response_probleme_csp(response)
    solution = solver_csp(variables, constraints)
    if solution != "\nAucune solution trouvée.\n":
        final_prompt = f"La solution au problème est la suivante: {solution}. Reformulez la réponse pour qu'elle soit bien présentée."
        final_response = llm2.invoke(final_prompt.format(solution=solution)).content
    else:
        final_prompt = f"Voici le problème: {problem_statement}\n Résout le problème s'il te plaît."
        final_response = llm2.invoke(final_prompt).content
    return final_response

# Définir la fonction pour résoudre les sudokus sur Reddit
def solve_sudoku_reddit(problem_statement: str) -> str:
    sudoku_grid_by_gpt = get_solver_sudoku_input(problem_statement)
    sudoku_grid = parse_sudoku_grid(sudoku_grid_by_gpt)
    start_time = timer()
    result = solver_sudoku_with_pulp('CHOCO', [], sudoku_grid)
    end_time = timer()
    execution_time = end_time - start_time
    solution = f"Solveur: CHOCO, Temps d'exécution: {execution_time} secondes\nLa solution est :\n{np.array(result)}\n"
    # final_prompt = f"La solution au problème est la suivante: {solution}. Reformulez la réponse pour qu'elle soit bien présentée."
    # final_response = llm.invoke(final_prompt.format(solution=solution))
    final_response = solution
    return final_response

# Définir la fonction pour résoudre les problèmes de planification sur Reddit
def solve_plan_reddit(problem_statement: str) -> str:
    response = get_planning_sat_input(problem_statement)
    variables, clauses = parse_json_response(response)
    # print("VARIABLES : ", variables)
    # print("CLAUSES : ", clauses)
    variable_names = {i+1: var_name for i, var_name in enumerate(variables.keys())}
    solution1 = solve_sat(clauses)
    solution2 = afficher_solution(solution1,variables, variable_names)
    # print("SOLUTION : ", solution2)
    final_prompt = f"Voici la question initial : {problem_statement}.La solution au problème est la suivante: {solution2}. Reformulez la réponse pour qu'elle soit bien présentée."
    final_response = llm2.invoke(final_prompt.format(solution=solution2)).content
    # print("final_response : ", final_response)
    return final_response

# Définir la fonction pour gérer les nouveaux posts
def handle_post(post):
    title = post.title
    if re.search(r"@botSCIA\s+/probleme$", title):
        print_post_details(post)
        problem_statement = post.selftext
        response = solve_csp_reddit(problem_statement)
        # print(response)
        post.reply(response)
    elif re.search(r"@botSCIA\s+/plan$", title):
        print_post_details(post)
        problem_statement = post.selftext
        response = solve_plan_reddit(problem_statement)
        post.reply(response)
        # print(response)
        print("Répondu au post.")
    elif re.search(r"@botSCIA\s+/sudoku$", title):
        print_post_details(post)
        sudoku_text = post.selftext
        response = solve_sudoku_reddit(sudoku_text)
        post.reply(response)
        print("Répondu au post.")
    elif re.search(r"@botSCIA\s*(/[^ ]+)?$", title):
        print_post_details(post)
        response = llm2.invoke(post.selftext).content
        # print(response)
        post.reply(response)
        print("Répondu au post.")

# Écouter les nouveaux posts
for post in subreddit.stream.submissions(skip_existing=True):
    handle_post(post)

################################---POUR TESTER SANS REDDIT---######################################

# CHOISI SI TU VEUX UN PROBLEME OU UN SUDOKU----------------------------------------------
# problem1 = "Nous devons répartir trois personnes, Alice, Bob et Charlie, dans trois salles (0, 1, et 2) de manière à ce que : Alice et Bob ne soient pas dans la même salle. La somme des indices des salles occupées par Alice, Bob et Charlie soit égale à 3."
# problem2 = "Vous devez vérifier s'il existe des entiers x et y tels que : x>5 𝑦<10 𝑥+𝑦=15"
# problem3 = """
# VOICI MON SUDOKU AHAHAHh
# OFZNEFOZUNEZOUN
# (0, 0, 0, 4, 0, 9, 6, 7, 0)
# (0, 0, 0, 0, 7, 6, 9, 0, 0)
# (0, 0, 0, 0, 0, 0, 0, 0, 3)

# (0, 0, 0, 0, 0, 1, 7, 4, 0)
# (6, 4, 0, 0, 0, 0, 0, 1, 8)
# (0, 2, 1, 6, 0, 0, 0, 0, 0)

# (1, 0, 0, 0, 0, 0, 0, 0, 0)
# (0, 0, 4, 3, 2, 0, 0, 0, 0)
# (0, 6, 2, 9, 0, 4, 0, 0, 0)

# """
# problem4 = """
# resout ce sudoku stp je compte sur toi
# ajajajaj
# fdzafeae

# _ _ _ | 4 _ 9 | 6 7 _
# _ _ _ | _ 7 6 | 9 _ _
# _ _ _ | _ _ _ | _ _ 3
# ---------------------
# _ _ _ | _ _ 1 | 7 4 _
# 6 4 _ | _ _ _ | _ 1 8
# _ 2 1 | 6 _ _ | _ _ _
# ---------------------
# 1 _ _ | _ _ _ | _ _ _
# _ _ 4 | 3 2 _ | _ _ _
# _ 6 2 | 9 _ 4 | _ _ _
# """
# problem5 = "Imaginons que nous avons quatre activités sportives A1, A2, A3 et A4 et trois créneaux horaires disponibles H1, H2 et H3. Nous voulons planifier ces activités de manière à ce que certains entraîneurs puissent les encadrer sans conflit d'horaire. Disons que :"

# "L'activité A1 doit être encadrée par l'entraîneur E1."
# "L'activité A2 doit être encadrée par l'entraîneur E2."
# "L'activité A3 doit être encadrée par l'entraîneur E3 ou E4."
# "L'activité A4 doit être encadrée par l'entraîneur E1 ou E3."
# "De plus, les contraintes sont les suivantes :"

# "Les activités A1 et A2 ne peuvent pas être programmées en même temps car E1 et E2 sont indisponibles en même temps."
# "L'activité A3 doit être programmée à un créneau différent de A4 si c'est E3 qui l'encadre."
# "L'activité A1 doit être programmée à un créneau différent de A4 si c'est E1 qui l'encadre."
# # Choisir le problème à résoudre
# problem_statement = problem5
# print("LE PROBLEME DE REDDIT : ", problem_statement)
# #PARTI PROBLEME PLAN -----------------------

# response = get_planning_sat_input(problem_statement)
# variables, clauses = parse_json_response(response)
# print("VARIABLES : ", variables)
# print("CLAUSES : ", clauses)
# variable_names = {i+1: var_name for i, var_name in enumerate(variables.keys())}
# solution1 = solve_sat(clauses)
# solution2 = afficher_solution(solution1,variables, variable_names)
# print("SOLUTION : ", solution2)
# final_prompt = f"Voici la question initial : {problem_statement}.La solution au problème est la suivante: {solution2}. Reformulez la réponse pour qu'elle soit bien présentée."
# final_response = llm2.invoke(final_prompt.format(solution=solution2)).content
# print("final_response : ", final_response)
# PARTIE PROBLEME CSP ----------------------------------------------
# Obtenir la réponse de ChatGPT
# response = get_solver_input(problem_statement)
# print("Réponse de ChatGPT :\n", response)
# # Parser la réponse pour obtenir les variables et contraintes
# variables, constraints = parse_response_probleme_csp(response)
# print("\nVariables :", variables)
# print("Contraintes :", constraints)
# # Utiliser les variables et contraintes avec le solver
# solution = solver_csp(variables, constraints)
# if (solution != "\nAucune solution trouvée.\n"):
#     print(f"ici: {solution}.")
#     final_prompt = f"La solution au problème est la suivante: {solution}. Reformulez la réponse pour qu'elle soit bien présentée."
#     final_response = llm.invoke(final_prompt.format(solution=solution))
#     print("finale_response WITH OUR SOLVER: ", final_response)
# else:
#     final_prompt = f"Voici le probleme {problem_statement}\n Résout le probleme avec une petite phrase stp."
#     final_response = llm.invoke(final_prompt.format(solution=solution))
#     print("finale_response of GPT ONLY: ", final_response)


# PARTIE SUDOKU CHOCO ----------------------------------------------
#Obtenir la réponse de ChatGPT
# response = get_solver_sudoku_input(problem_statement)
# print("Réponse de ChatGPT :\n", response)
# sudoku_grid = parse_sudoku_grid(problem_statement)
# print("SUDOKU APRES PARSING : ", sudoku_grid)
# # Mesurer le temps d'exécution pour chaque configuration
# start_time = timer()
# result = solver_sudoku_with_pulp('CHOCO', [], sudoku_grid)
# end_time = timer()
# execution_time = end_time - start_time
# solution = f"Solveur: CHOCO, Temps d'exécution: {execution_time} secondes\nLa solution est :\n{np.array(result)}\n"
# print("SOLUTION FINALE : ", solution)