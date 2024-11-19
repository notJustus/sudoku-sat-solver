import os

class Sudoku:
    def __init__(self, rules=None, constraints=None, clauses=None, grid_size=None, n_vars=None, filename=None) -> None:
        self.comment = []
        self.filename = filename if filename is not None else ""
        self.n_vars = n_vars if n_vars is not None else 0
        self.rules = rules if rules is not None else []
        self.constraints = constraints if constraints is not None else []
        self.clauses = clauses if clauses is not None else []
        self.assignments = {}
        self.satisfiable = True
        self.grid_size = grid_size if grid_size is not None else None
        self.split_vars = []
        self.candidate_vars = []
        #self.split_assignments = {}
        # Performence related
        self.runtime = 0.0
        self.n_backtracks = 0
        self.n_splits = 0

    def clone(self):
        from copy import deepcopy
        sudoku_copy = Sudoku(
            rules=deepcopy(self.rules),
            constraints=deepcopy(self.constraints),
            clauses=deepcopy(self.clauses),
            grid_size=self.grid_size,
            n_vars=self.n_vars
        )
        sudoku_copy.assignments = deepcopy(self.assignments)
        sudoku_copy.split_vars = deepcopy(self.split_vars)
        sudoku_copy.satisfiable = self.satisfiable
        return sudoku_copy
    
    def print_performence_stats(self):
        print(f"TR")


    def print_solved_sudoku(self):
        print(f"Solved Sudoku:\n")
        variables = {literal if value else -literal for literal, value in self.assignments.items() if value}
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


    def solution_to_dimac(self) -> list:
        all_variables = set()
        for row in range(1, self.grid_size + 1):
            for col in range(1, self.grid_size + 1):
                for val in range(1, self.grid_size + 1):
                    variable = int(f"{row}{col}{val}")
                    all_variables.add(variable)
        
        true_literals = {literal if value else -literal for literal, value in self.assignments.items() if value}
        assert len(self.assignments) == len(all_variables), "Not all variables assigned!"

        false_literals = {-literal for literal in all_variables if literal not in true_literals}

        dimac_clauses = list(true_literals) + list(false_literals)
        return dimac_clauses
    

    def output_solution(self):
        dimac_clauses = self.solution_to_dimac()
        n_vars = self.n_vars                
        n_clauses = len(dimac_clauses)            

        if not os.path.exists("output"):
            os.makedirs("output")
        output_file = f"output/{self.filename}.out"

        with open(output_file, 'w') as file:
            file.write(f"p cnf {n_vars} {n_clauses}\n")
            
            for clause in dimac_clauses:
                file.write(f"{clause} 0\n")



    def __str__(self):
        return (f"Sudoku CNF with {self.n_vars} variables, "
                f"{self.n_clauses} clauses, and comments:\n" +
                "\n".join(self.comment) + "\nClauses:\n" + "\n".join(map(str, self.clauses)) +
                "Constraints:\n" + "\n".join(map(str, self.assignments)))