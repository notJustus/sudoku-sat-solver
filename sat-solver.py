import os
import argparse
import math
import random
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

    return constraints


def remove_tautologies(sudoku: Sudoku):
    for clause in sudoku.clauses:
        literal_set = set(clause)

        # Tautology
        if any(-literal in literal_set for literal in literal_set):
            sudoku.clauses.remove(clause)


def handle_unit_clauses(sudoku: Sudoku):
    unit_clauses = [clause for clause in sudoku.clauses if len(clause) == 1]
    #print(f"Unit Clauses: {unit_clauses}\n")
    for clause in unit_clauses:
        unit_literal = clause[0]
        variable = abs(unit_literal)
        value = unit_literal > 0

        sudoku.assignments[variable] = value

    sudoku.clauses = [clause for clause in sudoku.clauses if len(clause) != 1]

    #print(f"Assignments: {sudoku.assignments}\n")
    true_literals = {literal if value else -literal for literal, value in sudoku.assignments.items() if value}
    false_literals = {-literal if value else literal for literal, value in sudoku.assignments.items() if not value}
    #print(f"True literals: {true_literals}\n")
    #print(f"False literals: {false_literals}\n")


    removed_clauses = []
    updated_clauses = []

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
                sudoku.satisfiable = False
            updated_clauses.append(modified_clause)

    unit_clauses_left = [clause for clause in updated_clauses if len(clause) == 1]
    sudoku.clauses = updated_clauses
    #print(f"UNIT LEFT: {unit_clauses_left}\n")
    #print(f"Removed clauses: {removed_clauses}\n")
    if unit_clauses_left:
        print(f"Recursion entered\n")
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



def splitting(sudoku: Sudoku):
    if all_clauses_satisfied(sudoku):
        print("Solution found!")
        return True

    if not all_clauses_consistent(sudoku):
        print("Conflict encountered, backtracking...")
        return False

    # Step 3: Perform unit propagation
    handle_unit_clauses(sudoku)

    # Step 4: Check if further simplification has satisfied the problem
    if all_clauses_satisfied(sudoku):
        print("Solution found after unit propagation!")
        return True

    variable = pick_random_variable(sudoku)
    sudoku.split_vars.remove(variable)

    # Step 6: Try assigning True and recursively solve
    print(f"Splitting on variable: {variable} with True")
    sudoku.assignments[variable] = True
    sudoku_cloned = sudoku.clone()  # Clone Sudoku for backtracking
    handle_unit_clauses(sudoku_cloned)
    #sudoku_cloned.clauses = simplify_formula(sudoku_cloned.clauses, variable, True)
    
    if splitting(sudoku_cloned):
        sudoku.assignments = sudoku_cloned.assignments
        return True

    # Step 7: Try assigning False if True didn't work
    print(f"Splitting on variable: {variable} with False")
    sudoku.assignments[variable] = False
    sudoku_cloned = sudoku.clone()  # Clone Sudoku for backtracking
    handle_unit_clauses(sudoku_cloned)
    #sudoku_cloned.clauses = simplify_formula(sudoku_cloned.clauses, variable, False)

    if splitting(sudoku_cloned):
        sudoku.assignments = sudoku_cloned.assignments
        return True

    # Step 8: If both fail, backtrack
    print(f"Backtracking on variable: {variable}")
    return False


def simplify_formula(clauses, variable, value):
    """
    Simplify the formula based on the given variable assignment.
    """
    true_literal = variable if value else -variable
    false_literal = -true_literal

    simplified_clauses = []
    for clause in clauses:
        if true_literal in clause:
            continue  # Clause is satisfied, skip it
        new_clause = [lit for lit in clause if lit != false_literal]
        simplified_clauses.append(new_clause)

    return simplified_clauses


def print_sudoku(variables):
    # Initialize a 9x9 grid with empty values (.)
    grid = [['.' for _ in range(9)] for _ in range(9)]
    
    # Loop through each variable in the list and place the value in the correct grid position
    for var in variables:
        row = (var // 100) - 1  # Get the row (subtract 1 to match 0-indexing)
        col = (var % 100) // 10 - 1  # Get the column (subtract 1 to match 0-indexing)
        value = var % 10  # Get the value (last digit)
        
        # Ensure row and col are within bounds
        if 0 <= row < 9 and 0 <= col < 9:
            grid[row][col] = str(value)
        else:
            print(f"Error: Invalid variable {var}, out of bounds.")

    # Print the Sudoku grid with lines separating 3x3 subgrids
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)  # Print a separator line after every 3 rows
        row_display = ""
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_display += " | "  # Add a vertical separator after every 3 columns
            row_display += grid[r][c] + " "
        print(row_display)



def simple_dpll(rules_file, puzzle_file, grid_size):
    # Encode rules and puzzle in dimacs
    rules = encode_rules_in_dimac(rules_file)
    constraints = encode_puzzle_in_dimacs(puzzle_file, grid_size)
    sudoku = Sudoku(
        rules=rules,
        constraints=constraints,
        clauses=rules+constraints,
        grid_size=grid_size,
        n_vars=grid_size*grid_size*grid_size
    )

    print(f"###Num of rules: {len(sudoku.rules)}\n")
    print(f"###Num of constraints: {len(sudoku.constraints)}\n")
    print(f"###Num of clauses: {len(sudoku.clauses)}\n")
    init_simplification(sudoku)
    print(f"### INIT DONE, Clauses Left: {len(sudoku.clauses)}\n")

    if not sudoku.satisfiable:
        print(f"###Sudoku not satisfiable!\n")
        return
    
    if(not all_clauses_satisfied(sudoku)):
        print(f"-> Not all clauses satisfied!\n")

    get_candidate_variables(sudoku)

    splitting(sudoku)

    true_literals = {literal if value else -literal for literal, value in sudoku.assignments.items() if value}
    print(f"###SOLUTION: {true_literals}\n")
    print_sudoku(true_literals)


    print(f"###Num of clauses END: {len(sudoku.clauses)}\n")
    # Simplify Clauses
    #result = dpll(sudoku)
    #if result:
    #    print(f"Solution found: {sudoku.assignments}")
    #else:
    #    print("No solution found.")


def get_grid_size(puzzle_path):
    with open(puzzle_path, 'r') as f:
        first_line = f.readline().strip()
    grid_size = int(math.sqrt(len(first_line)))

    assert(grid_size == 4 or grid_size == 9 or grid_size == 16), "Invalid grid size"

    return grid_size



# Check for the empty clause -> a unit clause that evaluates to FALSE 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--strategy", type=int, default=1, help="n=1 for basic DP")
    parser.add_argument("--puzzle_file", type=str)
    args = parser.parse_args()

    grid_size = get_grid_size(args.puzzle_file)
    rules_file = f"rules/sudoku-rules-{grid_size}x{grid_size}.txt"
    print(f"RULES FILE: {rules_file}\n")

    if args.strategy == 1:
        simple_dpll(rules_file, args.puzzle_file, grid_size)
    elif args.strategy == 2:
        pass
    elif args.strategy == 3:
        pass