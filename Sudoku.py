class Sudoku:
    def __init__(self) -> None:
        self.comment = []
        self.n_vars = 0
        self.n_clauses = 0
        self.rules = []
        self.assignments = []

    def __str__(self):
        return (f"Sudoku CNF with {self.n_vars} variables, "
                f"{self.n_clauses} clauses, and comments:\n" +
                "\n".join(self.comment) + "\nClauses:\n" + "\n".join(map(str, self.clauses)) +
                "Constraints:\n" + "\n".join(map(str, self.assignments)))