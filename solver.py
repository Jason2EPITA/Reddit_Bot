import re
from ortools.sat.python import cp_model
from config import llm
import ast
import os
import sys
import pulp
from config import get_choco_solver_path

choco_solver_path = get_choco_solver_path()

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

def get_solver_sudoku_input(problem_statement: str) -> str:
    """
    Envoie un prompt à ChatGPT et obtient la réponse.

    Args:
    - problem_statement (str): La description du problème en français.

    Returns:
    - response (str): La réponse de ChatGPT contenant les variables et les contraintes.
    """
    prompt = f"""
    voici un probleme de sudoku :
    "{problem_statement}"

    je veux que tu me renvoie le sudoku seulement (necris rien dautre) sous cete forme :
    _ _ _ | 4 _ 9 | 6 7 _
    _ _ _ | _ 7 6 | 9 _ _
    _ _ _ | _ _ _ | _ _ 3
    ---------------------
    _ _ _ | _ _ 1 | 7 4 _
    6 4 _ | _ _ _ | _ 1 8
    _ 2 1 | 6 _ _ | _ _ _
    ---------------------
    1 _ _ | _ _ _ | _ _ _
    _ _ 4 | 3 2 _ | _ _ _
    _ 6 2 | 9 _ 4 | _ _ _

    N'oublie pas de mettre des _ au lieu des 0 (je veux le meme format !)
    """

    response = llm.invoke(prompt)  # Utilisation de invoke
    return response

# Fonction pour parser la réponse de ChatGPT CSP et extraire les variables et contraintes
def parse_response_probleme_csp(response: str) -> tuple[list[str], list[str]]:
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

#Fonction pour résoudre le problème CSP en utilisant les variables et les contraintes fournies
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

#Fonction pour résoudre le sudoku en utilisant un solveur de Pulp
def solver_sudoku_with_pulp(solver, options, instance):
    N = 9 
    problem = pulp.LpProblem("SudokuSolver", pulp.LpMinimize)
    choices = pulp.LpVariable.dicts("Choice", (range(N), range(N), range(1, N + 1)), cat="Binary")

    problem += 0, "Arbitrary Objective"

    for r in range(N):
        for c in range(N):
            problem += pulp.lpSum([choices[r][c][v] for v in range(1, N + 1)]) == 1

    for v in range(1, N + 1):
        for r in range(N):
            problem += pulp.lpSum([choices[r][c][v] for c in range(N)]) == 1
            problem += pulp.lpSum([choices[c][r][v] for c in range(N)]) == 1

        for r in range(0, N, 3):
            for c in range(0, N, 3):
                problem += pulp.lpSum([choices[r + i][c + j][v] for i in range(3) for j in range(3)]) == 1

    for r in range(N):
        for c in range(N):
            if instance[r][c] != 0:
                problem += choices[r][c][instance[r][c]] == 1

    # Lookup table pour les solveurs
    solver_lookup = {
        "GLPK_CMD": lambda: problem.solve(pulp.PULP_CBC_CMD(msg=False, options=options)),
        "PYGLPK": lambda: problem.solve(pulp.PYGLPK(msg=False, options=options)),
        "CPLEX_CMD": lambda: problem.solve(pulp.CPLEX_CMD(msg=False, options=options)),
        "CPLEX_PY": lambda: problem.solve(pulp.CPLEX_PY(msg=False, options=options)),
        "GUROBI": lambda: problem.solve(pulp.GUROBI(msg=False, options=options)),
        "GUROBI_CMD": lambda: problem.solve(pulp.GUROBI_CMD(msg=False, options=options)),
        "MOSEK": lambda: problem.solve(pulp.MOSEK(msg=False, options=options)),
        "XPRESS": lambda: problem.solve(pulp.XPRESS(msg=False, options=options)),
        "CBC": lambda: problem.solve(pulp.PULP_CBC_CMD(msg=False, options=options)),
        "COIN_CMD": lambda: problem.solve(pulp.COIN_CMD(msg=False, options=options)),
        "COINMP_DLL": lambda: problem.solve(pulp.COINMP_DLL(msg=False, options=options)),
        "CHOCO": lambda: problem.solve(pulp.CHOCO_CMD(path=choco_solver_path, msg=False, keepFiles=True, options=options)),
        "MIPCL_CMD": lambda: problem.solve(pulp.MIPCL_CMD(msg=False, options=options)),
        "SCIP_CMD": lambda: problem.solve(pulp.SCIP_CMD(msg=False, options=options)),
        "FSCIP_CMD": lambda: problem.solve(pulp.FSCIP_CMD(msg=False, options=options)),
        "SCIP_PY": lambda: problem.solve(pulp.SCIP_PY(msg=False, options=options)),
        "HiGHS": lambda: problem.solve(pulp.HiGHS(msg=False, options=options)),
        "HiGHS_CMD": lambda: problem.solve(pulp.HiGHS_CMD(msg=False, options=options)),
        "COPT": lambda: problem.solve(pulp.COPT(msg=False, options=options)),
        "COPT_DLL": lambda: problem.solve(pulp.COPT_DLL(msg=False, options=options)),
        "COPT_CMD": lambda: problem.solve(pulp.COPT_CMD(msg=False, options=options))
    }

    # Exécute la fonction appropriée selon le solveur donné
    solver_function = solver_lookup.get('CHOCO')
    if solver_function:
        solver_function()
    else:
        raise ValueError(f"Solveur inconnu : {solver}")

    solution = [[0 for _ in range(N)] for _ in range(N)]
    for r in range(N):
        for c in range(N):
            for v in range(1, N + 1):
                if pulp.value(choices[r][c][v]) == 1:
                    solution[r][c] = v

    if os.path.exists("SudokuSolver-pulp.mps"):
        os.remove("SudokuSolver-pulp.mps")
    if os.path.exists("SudokuSolver-pulp.sol"):
        os.remove("SudokuSolver-pulp.sol")
    
    return solution

# Fonction pour parser la réponse de ChatGPT Sudoku et extraire la grille de sudoku
def parse_sudoku_grid(sudoku_string: str) -> tuple[tuple[int, ...], ...]:
    lines = sudoku_string.strip().split('\n')
    grid = []
    for line in lines:
        row = []
        for char in line:
            if char.isdigit():
                row.append(int(char))
            elif char == '_':
                row.append(0)
        if row:  # Ajoute cette condition pour ignorer les lignes vides
            grid.append(tuple(row))
    return tuple(grid)
