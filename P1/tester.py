import time
import random
import os
import math
import matplotlib.pyplot as plt
from sequential import SequentialFile, Record 

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

def run_performance_test():
    filename = "test_sequential.bin"
  
    if os.path.exists(filename): 
        os.remove(filename)


    sf = SequentialFile(filename)
    
    # Métricas
    insertion_times = []
    search_times = []
    range_times = []
    delete_times = []
    
    # 1. Prueba de Inserción (1000 registros)
    print("Midiendo inserciones...")
    for i in range(1, 1001):
        rec = generate_random_record(i)
        start = time.perf_counter()
        sf.insert(rec)
        end = time.perf_counter()
        insertion_times.append(end - start)

    # 2. Prueba de Búsqueda Puntual
    print("Midiendo búsquedas...")
    for _ in range(100):
        target_id = random.randint(1, 1000)
        start = time.perf_counter()
        sf.search(target_id)
        end = time.perf_counter()
        search_times.append(end - start)

    # 3. Prueba de Búsqueda por Rango
    print("Midiendo rangos...")
    for _ in range(50):
        start_id = random.randint(1, 800)
        start = time.perf_counter()
        sf.range_search(start_id, start_id + 100)
        end = time.perf_counter()
        range_times.append(end - start)

    # 4. Prueba de Eliminación
    print("Midiendo eliminaciones...")
    for _ in range(50):
        target_id = random.randint(1, 1000)
        start = time.perf_counter()
        sf.delete(target_id)
        end = time.perf_counter()
        delete_times.append(end - start)

    sf.close()
    return insertion_times, search_times, range_times, delete_times

if __name__ == "__main__":
    try:
        ins, sea, ran, del_t = run_performance_test()

        # Generar Gráfico
        plt.figure(figsize=(10, 6))
        plt.boxplot([ins, sea, ran, del_t], labels=['Inserción', 'Búsqueda', 'Rango', 'Eliminación'])
        plt.title('Tiempos de Acceso: Sequential File (Segundos)')
        plt.ylabel('Tiempo (Log Scale)')
        plt.yscale('log') 
        plt.grid(True, linestyle='--', alpha=0.7)
        print("Cerrando y mostrando gráfico...")    
        plt.show()
    except Exception as e:
        print(f"Ocurrió un error: {e}")