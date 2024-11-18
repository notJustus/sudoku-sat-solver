class Sudoku:
    def __init__(self, rules=None, constraints=None, clauses=None, grid_size=None) -> None:
        self.comment = []
        self.n_vars = 0
        self.rules = rules if rules is not None else []
        self.constraints = constraints if constraints is not None else []
        self.clauses = clauses if clauses is not None else []
        self.assignments = {}
        self.satisfiable = True
        self.grid_size = grid_size if grid_size is not None else None

    def __str__(self):
        return (f"Sudoku CNF with {self.n_vars} variables, "
                f"{self.n_clauses} clauses, and comments:\n" +
                "\n".join(self.comment) + "\nClauses:\n" + "\n".join(map(str, self.clauses)) +
                "Constraints:\n" + "\n".join(map(str, self.assignments)))