import multiprocessing as mp
import subprocess
import os


def run_bse(_):
    # Replace with the correct path to your venv Python and bse.py file
    subprocess.run([
        r"C:\Users\keeganhill\GetLifeTogether\Algo\.venv\Scripts\python.exe",
        r"C:\Users\keeganhill\Documents\ALGO\BristolStockExchange-master\bse.py"
    ])


if __name__ == '__main__':
    mp.freeze_support()  # Required for Windows

    num_runs = mp.cpu_count()

    with mp.Pool(processes=num_runs) as pool:
        pool.map(run_bse, range(num_runs))
