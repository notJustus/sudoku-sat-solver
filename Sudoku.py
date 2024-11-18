class Sudoku:
    def __init__(self, rules=None, constraints=None, clauses=None, grid_size=None, n_vars=None) -> None:
        self.comment = []
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

    def __str__(self):
        return (f"Sudoku CNF with {self.n_vars} variables, "
                f"{self.n_clauses} clauses, and comments:\n" +
                "\n".join(self.comment) + "\nClauses:\n" + "\n".join(map(str, self.clauses)) +
                "Constraints:\n" + "\n".join(map(str, self.assignments)))