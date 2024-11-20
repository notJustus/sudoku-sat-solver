import os
import argparse
import math
import random
import time
from Sudoku import Sudoku


def get_grid_size(puzzle_path):
    with open(puzzle_path, 'r') as f:
        first_line = f.readline().strip()
    grid_size = int(math.sqrt(len(first_line)))

    assert(grid_size == 4 or grid_size == 9 or grid_size == 16), "Invalid grid size"

    return grid_size


def encode_rules_in_dimac(rules_path: str):
    rules = []

    with open(rules_path, 'r') as f:
        for line in f:
            line = line.strip()

            if not line.startswith('c') and not line.startswith('p'):
                clause = list(map(int, line.split()[:-1]))
                rules.append(clause)

    return rules


def encode_puzzle_in_dimacs(puzzle, grid_size: int = 4):
    constraints = []
    
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


def encode_rules_and_constraints(rules_file, puzzle_file, grid_size):
    rules = encode_rules_in_dimac(rules_file)
    with open(puzzle_file, 'r') as f:
        puzzle = f.readline().strip()
    constraints = encode_puzzle_in_dimacs(puzzle, grid_size)
    sudoku = Sudoku(
        rules=rules,
        constraints=constraints,
        clauses=rules+constraints,
        grid_size=grid_size,
        n_vars=grid_size*grid_size*grid_size,
        filename=os.path.splitext(os.path.basename(puzzle_file))[0]
    )

    sudoku.init_simplification()

    if not sudoku.satisfiable:
        print(f"Sudoku not satisfiable!\n")
        return
    
    return sudoku


def select_heuristic(strategy, sudoku: Sudoku):
    if strategy == 1:
        sudoku.basic_dpll()
    elif strategy == 2:
        sudoku.mom_dpll()
    elif strategy == 3:
        sudoku.vsids_dpll()


def test_sudokus(rules_file, puzzle_file, grid_size):
    rules = encode_rules_in_dimac(rules_file)
    sudoku_id = 0

    with open(puzzle_file, 'r') as f:
        for sudoku in f:
            puzzle = sudoku.strip()
            constraints = encode_puzzle_in_dimacs(puzzle, grid_size)
            print(f"Testing Sudoku: {sudoku_id}\n")
            sudoku = Sudoku(
                id=sudoku_id,
                rules=rules,
                constraints=constraints,
                clauses=rules+constraints,
                grid_size=grid_size,
                n_vars=grid_size*grid_size*grid_size,
                filename=os.path.splitext(os.path.basename(puzzle_file))[0],
                heuristic_id=1
            )
            sudoku.init_simplification()

            if not sudoku.satisfiable:
                print(f"Sudoku not satisfiable!\n")
                return
            print("Basic Heuristic\n")
            sudoku.basic_dpll()
            sudoku = Sudoku(
                id=sudoku_id,
                rules=rules,
                constraints=constraints,
                clauses=rules+constraints,
                grid_size=grid_size,
                n_vars=grid_size*grid_size*grid_size,
                filename=os.path.splitext(os.path.basename(puzzle_file))[0],
                heuristic_id=2
            )
            sudoku.init_simplification()

            if not sudoku.satisfiable:
                print(f"Sudoku not satisfiable!\n")
                return
            print("MOM\n")
            sudoku.mom_dpll()
            sudoku = Sudoku(
                id=sudoku_id,
                rules=rules,
                constraints=constraints,
                clauses=rules+constraints,
                grid_size=grid_size,
                n_vars=grid_size*grid_size*grid_size,
                filename=os.path.splitext(os.path.basename(puzzle_file))[0],
                heuristic_id=3
            )
            sudoku.init_simplification()

            if not sudoku.satisfiable:
                print(f"Sudoku not satisfiable!\n")
                return
            print("VSIDS\n")
            sudoku.vsids_dpll()
            sudoku_id += 1

                


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--strategy", type=int, default=1, help="n=1 for basic DP, n=2 for MOM's heuristic, n=3 for VSIDS heuristic")
    parser.add_argument("--puzzle_file", type=str)
    args = parser.parse_args()

    grid_size = get_grid_size(args.puzzle_file)
    rules_file = f"rules/sudoku-rules-{grid_size}x{grid_size}.txt"

    test_sudokus(rules_file, args.puzzle_file, grid_size)
    #sudoku = encode_rules_and_constraints(rules_file, args.puzzle_file, grid_size)
    #select_heuristic(args.strategy, sudoku)
