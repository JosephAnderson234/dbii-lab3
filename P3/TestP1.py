import time
import random
import os
import matplotlib.pyplot as plt
from P1.sequential import SequentialFile, Record

def generate_random_record(id_val):
    return Record(
        id=id_val,
        name=f"Employee_{id_val}",
        age=random.randint(20, 60),
        country="Peru",
        department="Engineering",
        position="Staff",
        salary=2500.0 + id_val,
        joining_date="10/04/2026"
    )

def run_performance_test(num_records):
    filename = f"test_sequential_{num_records}.bin"
    if os.path.exists(filename): os.remove(filename)
    sf = SequentialFile(filename)
    
    metrics = {'Inserción': [], 'Búsqueda': [], 'Rango': [], 'Eliminación': []}
    
    print(f"\n--- Probando Sequential File con {num_records} registros ---")
    
    # 1. Inserción 
    for i in range(1, num_records + 1):
        rec = generate_random_record(i)
        start = time.perf_counter()
        sf.insert(rec)
        metrics['Inserción'].append(time.perf_counter() - start)

    # 2. Búsqueda Puntual 
    for _ in range(100):
        target_id = random.randint(1, num_records)
        start = time.perf_counter()
        sf.search(target_id)
        metrics['Búsqueda'].append(time.perf_counter() - start)

    # 3. Rango
    for _ in range(50):
        start_id = random.randint(1, max(1, num_records - 100))
        start = time.perf_counter()
        sf.range_search(start_id, start_id + 100)
        metrics['Rango'].append(time.perf_counter() - start)

    # 4. Eliminación 
    for _ in range(50):
        target_id = random.randint(1, num_records)
        start = time.perf_counter()
        sf.delete(target_id)
        metrics['Eliminación'].append(time.perf_counter() - start)

    sf.close()
    return metrics

def plot_results(metrics, num_records, type_file):
    plt.figure(figsize=(10, 6))
    plt.boxplot([metrics['Inserción'], metrics['Búsqueda'], metrics['Rango'], metrics['Eliminación']], 
                labels=['Inserción', 'Búsqueda', 'Rango', 'Eliminación'])
    plt.yscale('log')
    plt.title(f'Desempeño {type_file}: {num_records} Registros (Escala Log)')
    plt.ylabel('Tiempo (segundos)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f"{type_file.lower().replace(' ', '_')}_{num_records}.png")
    plt.close()

if __name__ == "__main__":
    for size in [100, 1000, 10000]:
        results = run_performance_test(size)
        plot_results(results, size, "Sequential File")
    print("\nGráficos del Sequential File generados con éxito.")