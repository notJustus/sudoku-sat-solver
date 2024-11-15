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


def apply_simplification():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--strategy", type=int, default=1, help="n=1 for basic DP")
    parser.add_argument("--grid_size", type=int, default=4, help="Number of cells in row/column")
    parser.add_argument("--rules_path", type=str)
    parser.add_argument("--puzzle_path", type=str)
    args = parser.parse_args()

    test = encode_rules_in_dimac(args.rules_path)
    constraints = encode_puzzle_to_dimacs(args.puzzle_path)
    test.assignments = constraints
    print(test)