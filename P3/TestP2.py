import time
import random
import os
import matplotlib.pyplot as plt
from P2.bst import BSTFile, Node

def generate_random_node(id_val):
    return Node(
        Employee_ID=id_val,
        Employee_Name=f"User_{id_val}",
        Age=random.randint(18, 70),
        Country="Peru",
        Department="Engineering",
        Position="Developer",
        Salary=float(random.randint(3000, 15000)),
        Joining_Date="12/04/2026"
    )

def run_performance_test(num_records):
    bin_path = f"performance_avl_{num_records}.bin"
    if os.path.exists(bin_path): os.remove(bin_path)
    tree = BSTFile(bin_path)
    
    metrics = {'Inserción': [], 'Búsqueda': [], 'Rango': [], 'Eliminación': []}
    
    print(f"\n--- Probando AVL File con {num_records} registros ---")
    
    ids = list(range(1, num_records + 1))
    random.shuffle(ids)
    
    # 1. Inserción
    for i in ids:
        node = generate_random_node(i)
        start = time.perf_counter()
        tree.insert(node)
        metrics['Inserción'].append(time.perf_counter() - start)

    # 2. Búsqueda Puntual
    for _ in range(100):
        target_id = random.randint(1, num_records)
        start = time.perf_counter()
        tree.search(target_id)
        metrics['Búsqueda'].append(time.perf_counter() - start)

    # 3. Rango 
    for _ in range(50):
        low = random.randint(1, max(1, num_records - 100))
        start = time.perf_counter()
        tree.range_search(low, low + 100)
        metrics['Rango'].append(time.perf_counter() - start)

    # 4. Eliminación 
    random.shuffle(ids)
    for i in ids[:50]:
        start = time.perf_counter()
        tree.delete(i)
        metrics['Eliminación'].append(time.perf_counter() - start)

    tree.close()
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
        plot_results(results, size, "AVL File")
    print("\nGráficos del AVL File generados con éxito.")