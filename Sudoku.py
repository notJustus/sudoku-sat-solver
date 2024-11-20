import os
import time
import random

class Sudoku:
    def __init__(self, rules=None, constraints=None, clauses=None, grid_size=None, n_vars=None, filename=None, heuristic_id=None, id=None) -> None:
        self.id = id if id is not None else -1
        self.heuristic_id = heuristic_id if heuristic_id is not None else -1
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
        self.variable_scores = {i: 0 for i in range(1, n_vars + 1)}
        self.conflicting_clauses = []
        #self.split_assignments = {}
        # Performence related
        self.runtime = 0.0
        self.n_backtracks = 0
        self.n_splits = 0
        self.n_conflicts = 0

    def clone(self):    
        from copy import deepcopy
        sudoku_copy = Sudoku(
            rules=deepcopy(self.rules),
            constraints=deepcopy(self.constraints),
            clauses=deepcopy(self.clauses),
            grid_size=self.grid_size,
            n_vars=self.n_vars
        )
        sudoku_copy.id = self.id
        sudoku_copy.heuristic_id = self.heuristic_id
        sudoku_copy.assignments = deepcopy(self.assignments)
        sudoku_copy.split_vars = deepcopy(self.split_vars)
        sudoku_copy.satisfiable = self.satisfiable
        sudoku_copy.runtime = self.runtime
        sudoku_copy.n_splits = self.n_splits
        sudoku_copy.n_backtracks = self.n_backtracks
        sudoku_copy.n_conflicts = self.n_conflicts
        sudoku_copy.variable_scores = self.variable_scores.copy()
        sudoku_copy.conflicting_clauses = self.conflicting_clauses.copy()
        return sudoku_copy
    

    def remove_tautologies(self):
        for clause in self.clauses:
            literal_set = set(clause)

            # Tautology
            if any(-literal in literal_set for literal in literal_set):
                self.clauses.remove(clause)

    
    def simplify_unit_clauses(self):
        unit_clauses = [clause for clause in self.clauses if len(clause) == 1]
        for clause in unit_clauses:
            unit_literal = clause[0]
            variable = abs(unit_literal)
            value = unit_literal > 0

            self.assignments[variable] = value

        self.clauses = [clause for clause in self.clauses if len(clause) != 1]

        true_literals = {literal if value else -literal for literal, value in self.assignments.items() if value}
        false_literals = {-literal if value else literal for literal, value in self.assignments.items() if not value}

        removed_clauses = []
        updated_clauses = []
        conflicting_clauses = []

        for clause in self.clauses:
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
                    self.satisfiable = False
                updated_clauses.append(modified_clause)

        unit_clauses_left = [clause for clause in updated_clauses if len(clause) == 1]
        self.clauses = updated_clauses

        if conflicting_clauses:
            self.conflicting_clauses.extend(conflicting_clauses)

        if unit_clauses_left:
            self.simplify_unit_clauses()


    def init_simplification(self):
        self.remove_tautologies()

        self.simplify_unit_clauses()


    def get_candidate_variables(self):
        all_variables = set()
        for row in range(1, self.grid_size + 1):
            for col in range(1, self.grid_size + 1):
                for val in range(1, self.grid_size + 1):
                    variable = int(f"{row}{col}{val}")
                    all_variables.add(variable)

        assigned_variables = set(self.assignments.keys())
        candidate_variables = list(all_variables - assigned_variables)
        self.split_vars = candidate_variables

            
    def all_clauses_satisfied(self):
        if not self.clauses:
            return True
        for clause in self.clauses:
            satisfied = False
            for literal in clause:
                variable = abs(literal)
                value = self.assignments.get(variable, None)

                if value is not None and ((literal > 0 and value) or (literal < 0 and not value)):
                    satisfied = True
                    break

            if not satisfied:
                return False

        return True 


    def all_clauses_consistent(self):
        return all(len(clause) > 0 for clause in self.clauses)
        for clause in sudoku.clauses:
            if len(clause) == 0:
                return False



    def splitting(self, heuristic):
        if self.all_clauses_satisfied():
            print("Solution found!")
            return True

        if not self.all_clauses_consistent():
            #print("Conflict encountered, backtracking...")
            self.n_conflicts += 1
            return False

        # Step 3: Perform unit propagation
        self.simplify_unit_clauses()

        # Step 4: Check if further simplification has satisfied the problem
        if self.all_clauses_satisfied():
            print("Solution found after unit propagation!")
            return True

        #variable = pick_random_variable(sudoku)
        variable = heuristic()
        if variable is None:
            return False
        print(f"Split Vars available before removal: {self.split_vars}")
        self.split_vars.remove(variable)

        # Step 6: Try assigning True and recursively solve
        #print(f"Splitting on variable: {variable} with True")
        self.n_splits += 1
        #self.assignments[variable] = True
        sudoku_cloned = self.clone()  # Clone Sudoku for backtracking
        sudoku_cloned.assignments[variable] = True
        sudoku_cloned.simplify_unit_clauses()
        
        if sudoku_cloned.splitting(heuristic):
            self.assignments = sudoku_cloned.assignments
            return True

        # Step 7: Try assigning False if True didn't work
        #print(f"Splitting on variable: {variable} with False")
        self.n_splits += 1
        #self.assignments[variable] = False
        sudoku_cloned = self.clone()  # Clone Sudoku for backtracking
        sudoku_cloned.assignments[variable] = False
        sudoku_cloned.simplify_unit_clauses()

        if sudoku_cloned.splitting(heuristic):
            self.assignments = sudoku_cloned.assignments
            return True

        # Step 8: If both fail, backtrack
        print(f"Backtracking on variable: {variable}")
        #del self.assignments[variable]
        self.n_backtracks += 1

        if self.conflicting_clauses:
            if heuristic == self.apply_vsids_heuristic:
                self.update_vsids_scores(self.conflicting_clauses)
                self.decay_vsids_scores()
            self.conflicting_clauses = []
            self.n_conflicts += 1
        return False




    # Heuristics

    # BASIC

    def pick_random_variable(self):
        return random.choice(self.split_vars)

    def basic_dpll(self):
        start_time = time.time()

        self.get_candidate_variables()

        self.splitting(self.pick_random_variable)

        end_time = time.time()
        self.runtime = end_time - start_time

        #self.print_solved_sudoku()
        self.output_solution()
        self.save_performence_stats()



    # MOM'S

    def apply_mom_heuristic(self):
        """
        Apply the Maximum Occurrence in the remaining clauses (MOM) heuristic
        to choose the next variable to split on.
        """
        # Step 1: Count the occurrences of each variable in the remaining clauses
        variable_count = {}

        for clause in self.clauses:
            for literal in clause:
                variable = abs(literal)  # Ignore the sign, consider only the variable itself
                #if variable not in self.assignments:  # Only consider unassigned variables
                if variable in self.split_vars:
                    if variable not in variable_count:
                        variable_count[variable] = 0
                    variable_count[variable] += 1

        # Step 2: Choose the variable that appears in the most clauses
        if variable_count:
            selected_variable = max(variable_count, key=variable_count.get)
            print(f"Selected variable (MOM heuristic): {selected_variable}")
            return selected_variable
        else:
            # If no unassigned variables, the puzzle is either solved or unsatisfiable
            print("No more variables to split on.")
            return None

    def mom_dpll(self):
        start_time = time.time()

        self.get_candidate_variables()

        self.splitting(self.apply_mom_heuristic)

        end_time = time.time()
        self.runtime = end_time - start_time

        #self.print_solved_sudoku()
        self.save_performence_stats()



    # VSIDS

    def update_vsids_scores(self, conflicting_clauses):
        """
        Increment the VSIDS score for variables in the conflicting clauses.
        """
        for clause in conflicting_clauses:
            for literal in clause:
                variable = abs(literal)
                if variable in self.variable_scores:
                    self.variable_scores[variable] += 1

    def decay_vsids_scores(self, decay_factor=0.95):
        """
        Apply decay to all VSIDS scores.
        """
        for variable in self.variable_scores:
            self.variable_scores[variable] *= decay_factor

    def apply_vsids_heuristic(self):
        """
        Select the variable with the highest VSIDS score.
        """
        unassigned_vars = [v for v in self.split_vars if v not in self.assignments]
        if not unassigned_vars:
            return None

        # Select the variable with the highest VSIDS score
        return max(unassigned_vars, key=lambda var: self.variable_scores.get(var, 0))

    def vsids_dpll(self):
        start_time = time.time()

        self.get_candidate_variables()

        self.splitting(self.apply_vsids_heuristic)

        end_time = time.time()
        self.runtime = end_time - start_time

        #self.print_solved_sudoku()
        self.save_performence_stats()




    def save_performence_stats(self):
        if not os.path.exists("results"):
            os.makedirs("results")

        stats_file_name = os.path.join("results", f"{self.filename}_heuristic_{self.heuristic_id}.txt")
        runtime = self.runtime

        stats_line = f"{self.id} {runtime:.2f} {self.n_backtracks} {self.n_splits} {self.n_conflicts}\n"

        with open(stats_file_name, "a") as stats_file:
            stats_file.write(stats_line)
        # filename_basic.txt
        # 0 12.0 13 0 



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