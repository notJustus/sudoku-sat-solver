import numpy as np

def calculate_statistics(file_paths):
    for file_path in file_paths:
        data = np.loadtxt(file_path)
        
        # Calculate mean and standard deviation for each column
        runtime_mean = np.mean(data[:, 1])
        runtime_std = np.std(data[:, 1])
        
        backtracks_mean = np.mean(data[:, 2])
        backtracks_std = np.std(data[:, 2])
        
        splits_mean = np.mean(data[:, 3])
        splits_std = np.std(data[:, 3])
        
        conflicts_mean = np.mean(data[:, 4])
        conflicts_std = np.std(data[:, 4])
        
        unit_clauses_resolved_mean = np.mean(data[:, 5])
        unit_clauses_resolved_std = np.std(data[:, 5])
        
        # Print the results for this heuristic
        heuristic_name = file_path.split('/')[-1].replace('.txt', '')
        print(f"Statistics for {heuristic_name}:")
        print(f"  Runtime: Mean = {runtime_mean:.2f}, Std = {runtime_std:.2f}")
        print(f"  Backtracks: Mean = {backtracks_mean:.2f}, Std = {backtracks_std:.2f}")
        print(f"  Splits: Mean = {splits_mean:.2f}, Std = {splits_std:.2f}")
        print(f"  Conflicts: Mean = {conflicts_mean:.2f}, Std = {conflicts_std:.2f}")
        print(f"  Unit Clauses Resolved: Mean = {unit_clauses_resolved_mean:.2f}, Std = {unit_clauses_resolved_std:.2f}")
        print('-' * 50)

# List the file paths for each heuristic result
file_paths = ['results/1000sudokus_heuristic_1.txt', 'results/1000sudokus_heuristic_2.txt', 'results/1000sudokus_heuristic_3.txt']
calculate_statistics(file_paths)
