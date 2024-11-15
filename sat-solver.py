import os
import argparse
from Sudoku import Sudoku


def encode_rules_in_dimac(rules_path: str) -> Sudoku:
    sudoku = Sudoku()

    with open(rules_path, 'r') as f:
        for line in f:
            line = line.strip()
             
            if line.startswith('c'):
                sudoku.comment.append(line[1:].strip())

            elif line.startswith('p'):
                parts = line.split()
                sudoku.n_vars = int(parts[2])
                sudoku.n_clauses = int(parts[3])

            else:
                clause = list(map(int, line.split()[:-1]))
                sudoku.rules.append(clause)

    return sudoku


def encode_puzzle_to_dimacs(puzzle_path: str, grid_size: int = 4):
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


def apply_simplification(sudoku: Sudoku):
    simplified_clauses = []
    
    for clause in sudoku.clauses:
        literal_set = set(clause)

        # Tautology
        if any(-literal in literal_set for literal in literal_set):
            continue

        # Unit Clause 
        if len(clause) == 1:
            unit_literal = clause[0]
            variable = abs(unit_literal)
            value = unit_literal > 0 
    
            sudoku.assignments[variable] = value
            continue

        simplified_clauses.append(clause)
    
    final_clauses = []

    for clause in simplified_clauses:
        simplified_clause = []

        if any(sudoku.assignments.get(abs(literal), None) == (literal > 0) for literal in clause):
            print(f"Removed satisfied clause: {clause}")
            continue

        for literal in clause:
            if sudoku.assignments.get(abs(literal), None) != (literal < 0):
                simplified_clause.append(literal)
            else:
                pass
                #print(f"Removed falsified literal {literal} from clause: {clause}")

        if simplified_clause:
            final_clauses.append(simplified_clause)

    sudoku.clauses = final_clauses

    
    # Pure Literal 



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--strategy", type=int, default=1, help="n=1 for basic DP")
    parser.add_argument("--grid_size", type=int, default=4, help="Number of cells in row/column")
    parser.add_argument("--rules_path", type=str)
    parser.add_argument("--puzzle_path", type=str)
    args = parser.parse_args()

    sudoku = encode_rules_in_dimac(args.rules_path)
    sudoku.constraints = encode_puzzle_to_dimacs(args.puzzle_path)
    sudoku.clauses = sudoku.rules + sudoku.constraints
    print(sudoku)
    print(f"## Number of Clauses {len(sudoku.clauses)}\n")
    apply_simplification(sudoku)
    print(f"## Number of Clauses {len(sudoku.clauses)}\n")