import multiprocessing as mp
import subprocess


def run_bse(_):
    
    subprocess.run([
        "/Users/keeganhill/GetLifeTogether/Algo/.venv/bin/python",  
        "/Users/keeganhill/Documents/ALGO/BristolStockExchange-master/bse.py"
    ])

if __name__ == '__main__':
    mp.freeze_support()
    mp.set_start_method("spawn", force=True)

    num_runs = mp.cpu_count()  # One run per core
    with mp.Pool(processes=num_runs) as pool:
        pool.map(run_bse, range(num_runs))
