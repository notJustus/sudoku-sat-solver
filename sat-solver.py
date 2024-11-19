import os
import argparse
import math
import random
import time
from Sudoku import Sudoku


def encode_rules_in_dimac(rules_path: str):
    rules = []

    with open(rules_path, 'r') as f:
        for line in f:
            line = line.strip()

            if not line.startswith('c') and not line.startswith('p'):
                clause = list(map(int, line.split()[:-1]))
                rules.append(clause)

    return rules


def encode_puzzle_in_dimacs(puzzle_path: str, grid_size: int = 4):
    constraints = []

    with open(puzzle_path, 'r') as f:
        puzzle = f.readline().strip()
    
    def encode_var(row, col, value):
        return 100 * (row + 1) + 10 * (col + 1) + value
    
    for r in range(grid_size):
        for c in range(grid_size):
            char = puzzle[r * grid_size + c]
            if char.isdigit():
                value = int(char)
                constraints.append([encode_var(r, c, value)])
            # TO-DO: Support for 16x16


    return constraints


def remove_tautologies(sudoku: Sudoku):
    for clause in sudoku.clauses:
        literal_set = set(clause)

        # Tautology
        if any(-literal in literal_set for literal in literal_set):
            sudoku.clauses.remove(clause)


def handle_unit_clauses(sudoku: Sudoku):
    unit_clauses = [clause for clause in sudoku.clauses if len(clause) == 1]
    for clause in unit_clauses:
        unit_literal = clause[0]
        variable = abs(unit_literal)
        value = unit_literal > 0

        sudoku.assignments[variable] = value

    sudoku.clauses = [clause for clause in sudoku.clauses if len(clause) != 1]

    true_literals = {literal if value else -literal for literal, value in sudoku.assignments.items() if value}
    false_literals = {-literal if value else literal for literal, value in sudoku.assignments.items() if not value}

    removed_clauses = []
    updated_clauses = []
    conflicting_clauses = []

    for clause in sudoku.clauses:
        modified_clause = []
        remove_clause = False

        for literal in clause:
            if literal in true_literals:
                removed_clauses.append(clause)
                remove_clause = True
                break
            elif literal in false_literals:
                continue
            elif abs(literal) in false_literals:
                remove_clause = True
                removed_clauses.append(clause)
                break
            elif abs(literal) in true_literals:
                continue
            else:
                modified_clause.append(literal)

        if not remove_clause:
            # If empty clause found, sudoku not satisfiable
            if not modified_clause:
                conflicting_clauses.append(clause)
                sudoku.satisfiable = False
            updated_clauses.append(modified_clause)

    unit_clauses_left = [clause for clause in updated_clauses if len(clause) == 1]
    sudoku.clauses = updated_clauses

    if conflicting_clauses:
        sudoku.conflicting_clauses.extend(conflicting_clauses)

    if unit_clauses_left:
        handle_unit_clauses(sudoku)


def init_simplification(sudoku: Sudoku):
    remove_tautologies(sudoku)

    handle_unit_clauses(sudoku)
 
        
def all_clauses_satisfied(sudoku: Sudoku):
    if not sudoku.clauses:
        return True
    for clause in sudoku.clauses:
        satisfied = False
        for literal in clause:
            variable = abs(literal)
            value = sudoku.assignments.get(variable, None)

            if value is not None and ((literal > 0 and value) or (literal < 0 and not value)):
                satisfied = True
                break

        if not satisfied:
            return False

    return True 


def all_clauses_consistent(sudoku: Sudoku):
    return all(len(clause) > 0 for clause in sudoku.clauses)
    for clause in sudoku.clauses:
        if len(clause) == 0:
            return False


def pick_random_variable(sudoku: Sudoku):
    return random.choice(sudoku.split_vars)


def get_candidate_variables(sudoku: Sudoku):
    all_variables = set()
    for row in range(1, sudoku.grid_size + 1):
        for col in range(1, sudoku.grid_size + 1):
            for val in range(1, sudoku.grid_size + 1):
                variable = int(f"{row}{col}{val}")
                all_variables.add(variable)

    assigned_variables = set(sudoku.assignments.keys())
    candidate_variables = list(all_variables - assigned_variables)
    sudoku.split_vars = candidate_variables


def apply_mom_heuristic(sudoku: Sudoku):
    """
    Apply the Maximum Occurrence in the remaining clauses (MOM) heuristic
    to choose the next variable to split on.
    """
    # Step 1: Count the occurrences of each variable in the remaining clauses
    variable_count = {}

    for clause in sudoku.clauses:
        for literal in clause:
            variable = abs(literal)  # Ignore the sign, consider only the variable itself
            if variable not in sudoku.assignments:  # Only consider unassigned variables
                if variable not in variable_count:
                    variable_count[variable] = 0
                variable_count[variable] += 1

    # Step 2: Choose the variable that appears in the most clauses
    if variable_count:
        selected_variable = max(variable_count, key=variable_count.get)
        #print(f"Selected variable (MOM heuristic): {selected_variable}")
        return selected_variable
    else:
        # If no unassigned variables, the puzzle is either solved or unsatisfiable
        print("No more variables to split on.")
        return None


def splitting(sudoku: Sudoku, heuristic):
    if all_clauses_satisfied(sudoku):
        print("Solution found!")
        return True

    if not all_clauses_consistent(sudoku):
        #print("Conflict encountered, backtracking...")
        return False

    # Step 3: Perform unit propagation
    handle_unit_clauses(sudoku)

    # Step 4: Check if further simplification has satisfied the problem
    if all_clauses_satisfied(sudoku):
        print("Solution found after unit propagation!")
        return True

    #variable = pick_random_variable(sudoku)
    variable = heuristic(sudoku)
    if variable is None:
        return False
    sudoku.split_vars.remove(variable)

    # Step 6: Try assigning True and recursively solve
    #print(f"Splitting on variable: {variable} with True")
    sudoku.n_splits += 1
    sudoku.assignments[variable] = True
    sudoku_cloned = sudoku.clone()  # Clone Sudoku for backtracking
    handle_unit_clauses(sudoku_cloned)
    
    if splitting(sudoku_cloned, heuristic):
        sudoku.assignments = sudoku_cloned.assignments
        return True

    # Step 7: Try assigning False if True didn't work
    #print(f"Splitting on variable: {variable} with False")
    sudoku.n_splits += 1
    sudoku.assignments[variable] = False
    sudoku_cloned = sudoku.clone()  # Clone Sudoku for backtracking
    handle_unit_clauses(sudoku_cloned)

    if splitting(sudoku_cloned, heuristic):
        sudoku.assignments = sudoku_cloned.assignments
        return True

    # Step 8: If both fail, backtrack
    #print(f"Backtracking on variable: {variable}")
    sudoku.n_backtracks += 1
    return False


def basic_dpll(sudoku: Sudoku):
    start_time = time.time()

    get_candidate_variables(sudoku)

    splitting(sudoku, pick_random_variable)

    end_time = time.time()
    sudoku.runtime = end_time - start_time

    sudoku.print_solved_sudoku()
    sudoku.output_solution()


def mom_dpll(sudoku: Sudoku):
    start_time = time.time()

    get_candidate_variables(sudoku)

    splitting(sudoku, apply_mom_heuristic)

    end_time = time.time()
    sudoku.runtime = end_time - start_time

    sudoku.print_solved_sudoku()




def update_vsids_scores(sudoku: Sudoku, conflicting_clauses):
    """
    Increment the VSIDS score for variables in the conflicting clauses.
    """
    for clause in conflicting_clauses:
        for literal in clause:
            variable = abs(literal)
            if variable in sudoku.variable_scores:
                sudoku.variable_scores[variable] += 1

def decay_vsids_scores(sudoku: Sudoku, decay_factor=0.95):
    """
    Apply decay to all VSIDS scores.
    """
    for variable in sudoku.variable_scores:
        sudoku.variable_scores[variable] *= decay_factor

def apply_vsids_heuristic(sudoku: Sudoku):
    """
    Select the variable with the highest VSIDS score.
    """
    unassigned_vars = [v for v in sudoku.split_vars if v not in sudoku.assignments]
    if not unassigned_vars:
        return None

    # Select the variable with the highest VSIDS score
    return max(unassigned_vars, key=lambda var: sudoku.variable_scores.get(var, 0))


def splitting_vsids(sudoku: Sudoku, heuristic):
    if all_clauses_satisfied(sudoku):
        print("Solution found!")
        return True

    if not all_clauses_consistent(sudoku):
        #print("Conflict encountered, backtracking...")
        return False

    # Step 3: Perform unit propagation
    handle_unit_clauses(sudoku)

    # Step 4: Check if further simplification has satisfied the problem
    if all_clauses_satisfied(sudoku):
        print("Solution found after unit propagation!")
        return True

    #variable = pick_random_variable(sudoku)
    variable = heuristic(sudoku)
    if variable is None:
        return False
    sudoku.split_vars.remove(variable)

    # Step 6: Try assigning True and recursively solve
    #print(f"Splitting on variable: {variable} with True")
    sudoku.n_splits += 1
    sudoku.assignments[variable] = True
    sudoku_cloned = sudoku.clone()  # Clone Sudoku for backtracking
    handle_unit_clauses(sudoku_cloned)
    
    if splitting(sudoku_cloned, heuristic):
        sudoku.assignments = sudoku_cloned.assignments
        return True

    # Step 7: Try assigning False if True didn't work
    #print(f"Splitting on variable: {variable} with False")
    sudoku.n_splits += 1
    sudoku.assignments[variable] = False
    sudoku_cloned = sudoku.clone()  # Clone Sudoku for backtracking
    handle_unit_clauses(sudoku_cloned)

    if splitting(sudoku_cloned, heuristic):
        sudoku.assignments = sudoku_cloned.assignments
        return True

    # Step 8: If both fail, backtrack
    #print(f"Backtracking on variable: {variable}")
    sudoku.n_backtracks += 1

    if sudoku.conflicting_clauses:
        update_vsids_scores(sudoku, sudoku.conflicting_clauses)
        decay_vsids_scores(sudoku)
        sudoku.conflicting_clauses = []
    
    return False


def vsids_dpll(sudoku: Sudoku):
    start_time = time.time()

    get_candidate_variables(sudoku)

    splitting_vsids(sudoku, apply_vsids_heuristic)

    end_time = time.time()
    sudoku.runtime = end_time - start_time

    sudoku.print_solved_sudoku()


def encode_rules_and_constraints(rules_file, puzzle_file, grid_size):
    rules = encode_rules_in_dimac(rules_file)
    constraints = encode_puzzle_in_dimacs(puzzle_file, grid_size)
    sudoku = Sudoku(
        rules=rules,
        constraints=constraints,
        clauses=rules+constraints,
        grid_size=grid_size,
        n_vars=grid_size*grid_size*grid_size,
        filename=os.path.splitext(os.path.basename(puzzle_file))[0]
    )

    init_simplification(sudoku)

    if not sudoku.satisfiable:
        print(f"Sudoku not satisfiable!\n")
        return
    
    return sudoku


def select_heuristic(strategy, sudoku):
    if strategy == 1:
        basic_dpll(sudoku)
    elif strategy == 2:
        mom_dpll(sudoku)
    elif strategy == 3:
        vsids_dpll(sudoku)


def get_grid_size(puzzle_path):
    with open(puzzle_path, 'r') as f:
        first_line = f.readline().strip()
    grid_size = int(math.sqrt(len(first_line)))

    assert(grid_size == 4 or grid_size == 9 or grid_size == 16), "Invalid grid size"

    return grid_size


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--strategy", type=int, default=1, help="n=1 for basic DP, n=2 for MOM's heuristic, n=3 for VSIDS heuristic")
    parser.add_argument("--puzzle_file", type=str)
    args = parser.parse_args()

    grid_size = get_grid_size(args.puzzle_file)
    rules_file = f"rules/sudoku-rules-{grid_size}x{grid_size}.txt"

    sudoku = encode_rules_and_constraints(rules_file, args.puzzle_file, grid_size)
    select_heuristic(args.strategy, sudoku)
