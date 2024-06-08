import re
from ortools.sat.python import cp_model
from config import llm
import ast

# Fonction pour envoyer un prompt à ChatGPT et obtenir la réponse
def get_solver_input(problem_statement: str) -> str:
    """
    Envoie un prompt à ChatGPT et obtient la réponse.

    Args:
    - problem_statement (str): La description du problème en français.

    Returns:
    - response (str): La réponse de ChatGPT contenant les variables et les contraintes.
    """
    prompt = f"""
    Voici un problème mathématique décrit en français :
    "{problem_statement}"

    Veuillez extraire et retourner les informations suivantes sous forme de code Python :
    1. Une liste de variables utilisées pour représenter le problème.
    2. Une liste de contraintes mathématiques sous forme de chaînes.

    Format de la sortie :
    variables = ['x', 'y', 'z']
    constraints = [
        "x != y",
        "x + y + z == 3"
    ]
    """

    response = llm.invoke(prompt)  # Utilisation de invoke
    return response

# Fonction pour parser la réponse de ChatGPT
def parse_response(response: str) -> tuple[list[str], list[str]]:
    """
    Parse la réponse de ChatGPT pour extraire les variables et les contraintes.

    Args:
    - response (str): La réponse de ChatGPT.

    Returns:
    - tuple: Une tuple contenant la liste des variables et la liste des contraintes.
    """
    # Utilisation d'expressions régulières pour extraire les variables et les contraintes
    variables_match = re.search(r"variables\s*=\s*(\[[^\]]*\])", response)
    constraints_match = re.search(r"constraints\s*=\s*(\[[^\]]*\])", response)

    # Vérifier si les correspondances ont été trouvées
    if variables_match and constraints_match:
        try:
            variables = ast.literal_eval(variables_match.group(1))
            constraints = ast.literal_eval(constraints_match.group(1))
            return variables, constraints
        except (ValueError, SyntaxError) as e:
            print(f"Erreur lors de l'évaluation de la chaîne : {e}")
            return [], []
    else:
        # Si aucune correspondance n'a été trouvée, renvoyer des valeurs par défaut
        return [], []
def solver_csp(variables: list[str], constraints: list[str]) -> str:
    """
    Résout le problème en utilisant les variables et contraintes fournies et renvoie la solution sous forme de string.

    Args:
    - variables (list[str]): La liste des variables.
    - constraints (list[str]): La liste des contraintes.

    Returns:
    - result (str): La solution formatée en string.
    """
    model = cp_model.CpModel()
    max_bound = 10**9  # Borne supérieure pour les variables

    # Créer les variables avec une borne supérieure élevée
    var_dict = {var: model.NewIntVar(0, max_bound, var) for var in variables}

    for constraint in constraints:
        formatted_constraint = constraint
        for var in variables:
            formatted_constraint = formatted_constraint.replace(var, f"var_dict['{var}']")
        model.Add(eval(formatted_constraint))

    solver = cp_model.CpSolver()

    # Utiliser le SolutionCollector pour enregistrer toutes les solutions
    class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
        def __init__(self, variables):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._variables = variables
            self._solutions = []

        def on_solution_callback(self):
            solution = {var: self.Value(var_dict[var]) for var in self._variables}
            self._solutions.append(solution)

        def solutions(self):
            return self._solutions

    solution_printer = VarArraySolutionPrinter(variables)
    solver.SearchForAllSolutions(model, solution_printer)

    result = "\nSolutions trouvées:\n"
    solutions = solution_printer.solutions()
    if len(solutions) > 1:
        for solution in solutions:
            result += "  " + ", ".join(f"{var} = {value}" for var, value in solution.items()) + "\n"
    else:
        result = "\nAucune solution trouvée.\n"

    return result
