import os
import argparse
import math
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
    print(f"Unit Clauses: {unit_clauses}\n")
    for clause in unit_clauses:
        unit_literal = clause[0]
        variable = abs(unit_literal)
        value = unit_literal > 0

        sudoku.assignments[variable] = value

    sudoku.clauses = [clause for clause in sudoku.clauses if len(clause) != 1]

    print(f"Assignments: {sudoku.assignments}\n")
    true_literals = {literal if value else -literal for literal, value in sudoku.assignments.items() if value}
    false_literals = {-literal if value else literal for literal, value in sudoku.assignments.items() if not value}
    print(f"True literals: {true_literals}\n")
    print(f"False literals: {false_literals}\n")


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
    print(f"UNIT LEFT: {unit_clauses_left}\n")
    print(f"Removed clauses: {removed_clauses}\n")
    if unit_clauses_left:
        print(f"Recursion entered\n")
        handle_unit_clauses(sudoku)


def apply_simplification(sudoku: Sudoku):

    remove_tautologies(sudoku)

    handle_unit_clauses(sudoku)


def dpll(sudoku: Sudoku):
    # 1. Simplify the clauses
    apply_simplification(sudoku)

    # 2. Check if all clauses are satisfied
    if all(any(sudoku.assignments.get(abs(literal), None) == (literal > 0) for literal in clause) for clause in sudoku.clauses):
        return True  # The formula is satisfied

    # 3. Check for an empty clause (unsatisfiable)
    if any(len(clause) == 0 for clause in sudoku.clauses):
        return False  # The formula is unsatisfiable

    # 4. Unit Propagation - if any unit clauses exist, apply them
    for clause in sudoku.clauses:
        if len(clause) == 1:
            unit_literal = clause[0]
            variable = abs(unit_literal)
            value = unit_literal > 0
            if variable not in sudoku.assignments:
                sudoku.assignments[variable] = value
            return dpll(sudoku)

    # 5. Pure Literal Elimination - if a literal appears only in one polarity, eliminate it
    all_literals = [literal for clause in sudoku.clauses for literal in clause]
    pure_literals = set()
    for literal in all_literals:
        if -literal not in all_literals:
            pure_literals.add(literal)

    if pure_literals:
        # Assign pure literals and simplify the formula
        literal = pure_literals.pop()
        variable = abs(literal)
        value = literal > 0
        if variable not in sudoku.assignments:
            sudoku.assignments[variable] = value
        return dpll(sudoku)

    # 6. Backtracking - Choose a literal, assign it, and recurse
    unassigned_variables = [i for i in range(1, sudoku.n_vars + 1) if i not in sudoku.assignments]
    if not unassigned_variables:
        return False  # If no unassigned variables, the formula is unsatisfiable

    variable = random.choice(unassigned_variables)
    for value in [True, False]:
        sudoku.assignments[variable] = value
        if dpll(sudoku):
            return True
        # If the current assumption leads to a contradiction, backtrack
        del sudoku.assignments[variable]

    return False



#def all_clauses_satisfied(sudoku: Sudoku):
    for clause in sudoku.clauses:
        for literal in clause:
            if not sudoku.assignments[literal]:
                return False
            
        
def all_clauses_satisfied(sudoku: Sudoku):
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
    for clause in sudoku.clauses:
        if len(clause) == 0:
            return False


def simple_dpll(rules_file, puzzle_file, grid_size):
    # Encode rules and puzzle in dimacs
    rules = encode_rules_in_dimac(rules_file)
    constraints = encode_puzzle_in_dimacs(puzzle_file)
    sudoku = Sudoku(
        rules=rules,
        constraints=constraints,
        clauses=rules+constraints,
        grid_size=grid_size
    )

    n_vars = (sudoku.grid_size * sudoku.grid_size) * sudoku.grid_size
    print(f"###Num of rules: {len(sudoku.rules)}\n")
    print(f"###Num of constraints: {len(sudoku.constraints)}\n")
    print(f"###Num of clauses: {len(sudoku.clauses)}\n")
    apply_simplification(sudoku)

    if not sudoku.satisfiable:
        print(f"Sudoku not satisfiable!\n")
        #return
    
    if(not all_clauses_satisfied(sudoku)):
        print(f"-> Not all clauses satisfied!\n")
    while not all_clauses_satisfied(sudoku):
        print(f"Keep splitting!\n")
        # Pick a variable and truth assignment
        assert(len(sudoku.assignments) == n_vars), "Already assigned truth values to all variables\n"
        

        # Simplify clauses

        # if inconsistent -> backtrack 
        # if satisfied -> finished


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