"""BST persistido en archivo binario.

El archivo comienza con una cabecera que contiene:
- size (int): número total de registros
- root_ptr (int): índice del nodo raíz (-1 si vacío)
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
import struct
import os
import csv

@dataclass
class Node:
    Employee_ID: int
    Employee_Name: str
    Age: int
    Country: str
    Department: str
    Position: str
    Salary: float
    Joining_Date: str
    # TODO: definir los campos del nodo
    id: int = 0
    left: int = -1
    right: int = -1
    height: int = 0

class BSTFile:
    HEADER_FORMAT = 'ii'
    NODE_FORMAT = 'i30si20s20s20sf10siiii'  

    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    NODE_SIZE = struct.calcsize(NODE_FORMAT)

    def __init__(self, filename: str):
        """Inicializa la instancia sobre filename.

        - Debe abrir/crear el archivo en modo binario lectura/escritura.
        - Si el archivo es nuevo, debe inicializar la cabecera con size=0 y root_ptr=-1.
        """
        self.filename = filename
        if not os.path.exists(filename):
            self.file = open(filename, 'wb+')
            self._write_header(0, -1)
        else:
            self.file = open(filename, 'rb+')
        self.size, self.root_ptr = self._read_header()
        self.node_format = self.NODE_FORMAT
        self.record_size = self.NODE_SIZE

    def _read_header(self) -> Tuple[int, int]:
        """Lee y devuelve (size, root_ptr) desde la cabecera del archivo."""
        self.file.seek(0)
        data = self.file.read(self.HEADER_SIZE)
        if len(data) != self.HEADER_SIZE:
            raise ValueError("Invalid header")
        return struct.unpack(self.HEADER_FORMAT, data)

    def _write_header(self, size: int, root_ptr: int) -> None:
        """Escribe la cabecera (size, root_ptr) en el archivo."""
        data = struct.pack(self.HEADER_FORMAT, size, root_ptr)
        self.file.seek(0)
        self.file.write(data)

    def _node_offset(self, index: int) -> int:
        """Calcula el offset byte donde se almacena el nodo index en el archivo.

        Se asume una asignación por índice (por ejemplo, el primer nodo tiene index 0,
        y su offset es HEADER_SIZE + 0 * NODE_SIZE).
        """
        return self.HEADER_SIZE + index * self.NODE_SIZE

    def _pack_node(self, node: Node) -> bytes:
        """Empaqueta un Node en bytes según NODE_FORMAT."""
        return struct.pack(
        self.NODE_FORMAT,
        node.Employee_ID,
        node.Employee_Name.encode().ljust(30, b' '),
        node.Age,
        node.Country.encode().ljust(20, b' '),
        node.Department.encode().ljust(20, b' '),
        node.Position.encode().ljust(20, b' '),
        node.Salary,
        node.Joining_Date.encode().ljust(10, b' '),
        node.id,
        node.left,
        node.right,
        node.height
    )

    def _unpack_node(self, data: bytes) -> Node:
        """Desempaqueta bytes en una instancia de Node."""
        res = struct.unpack(self.NODE_FORMAT, data)
        return Node(
            Employee_ID    = res[0],
            Employee_Name  = res[1].decode().strip(),
            Age            = res[2],
            Country        = res[3].decode().strip(),
            Department     = res[4].decode().strip(),
            Position       = res[5].decode().strip(),
            Salary         = res[6],
            Joining_Date   = res[7].decode().strip(),
            id             = res[8],
            left           = res[9],
            right          = res[10],
            height         = res[11]
        )

    def _read_node(self, index: int) -> Node:
        """Lee el nodo en el índice dado y devuelve una instancia de Node."""
        offset = self._node_offset(index)
        self.file.seek(offset)
        data = self.file.read(self.NODE_SIZE)
        if len(data) != self.NODE_SIZE:
            raise ValueError("Invalid node data")
        return self._unpack_node(data)

    def get_node(self, index: int) -> Node:
        """Alias para leer un nodo por su índice."""
        return self._read_node(index)

    def _write_node(self, index: int, node: Node) -> None:
        """Escribe un nodo en su posición correspondiente."""
        self.file.seek(self._node_offset(index))
        self.file.write(self._pack_node(node))

    def _get_height(self, index: int) -> int:
        if index == -1:
            return 0
        return self.get_node(index).height

    def _update_height(self, index: int):
        node = self.get_node(index)
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        # Importante: sobrescribir el nodo con la nueva altura
        self.file.seek(self._node_offset(index))
        self.file.write(self._pack_node(node))

    def _get_balance(self, index: int) -> int:
        if index == -1: 
            return 0
        node = self.get_node(index)
        return self._get_height(node.left) - self._get_height(node.right)

    def _rotate_right(self, y_idx: int) -> int:
        y = self._read_node(y_idx)
        x_idx = y.left
        x = self._read_node(x_idx)
        t2_idx = x.right

        # Realizar rotación
        x.right = y_idx
        y.left = t2_idx

        # Escribir cambios a disco
        self._write_node(y_idx, y)
        self._write_node(x_idx, x)

        # Actualizar alturas en disco
        self._update_height(y_idx)
        self._update_height(x_idx)

        return x_idx

    def _rotate_left(self, x_idx: int) -> int:
        x = self._read_node(x_idx)
        y_idx = x.right
        y = self._read_node(y_idx)
        t2_idx = y.left

        # Realizar rotación
        y.left = x_idx
        x.right = t2_idx

        # Escribir cambios a disco
        self._write_node(x_idx, x)
        self._write_node(y_idx, y)

        # Actualizar alturas en disco
        self._update_height(x_idx)
        self._update_height(y_idx)

        return y_idx

    def _insert_recursive(self, current_idx, new_idx) -> int:
        if current_idx == -1:
            return new_idx

        current_node = self._read_node(current_idx)
        new_node = self._read_node(new_idx)

        if new_node.Employee_ID < current_node.Employee_ID:
            current_node.left = self._insert_recursive(current_node.left, new_idx)
        else:
            current_node.right = self._insert_recursive(current_node.right, new_idx)

        # Escribir el nodo actualizado a disco
        self._write_node(current_idx, current_node)

        # Actualizar altura y balancear
        self._update_height(current_idx)
        balance = self._get_balance(current_idx)

        # Rotaciones
        if balance > 1 and new_node.Employee_ID < self._read_node(current_node.left).Employee_ID:
            return self._rotate_right(current_idx)
        if balance < -1 and new_node.Employee_ID > self._read_node(current_node.right).Employee_ID:
            return self._rotate_left(current_idx)
        if balance > 1 and new_node.Employee_ID > self._read_node(current_node.left).Employee_ID:
            current_node.left = self._rotate_left(current_node.left)
            self._write_node(current_idx, current_node)
            return self._rotate_right(current_idx)
        if balance < -1 and new_node.Employee_ID < self._read_node(current_node.right).Employee_ID:
            current_node.right = self._rotate_right(current_node.right)
            self._write_node(current_idx, current_node)
            return self._rotate_left(current_idx)
        return current_idx

    def insert(self, node: Node) -> int:
        """Inserta node en el árbol persistente.

        Debe:
        - Escribir el nodo al final (o en una posición libre según diseño).
        - Actualizar punteros left/right de los nodos padre según correspondan.
        - Actualizar la cabecera size y, si corresponde, root_ptr.

        Retorna el índice (o puntero) donde se almacenó el nodo.
        """
        if self.root_ptr != -1 and self.search(node.Employee_ID) is not None:
            return -1
        new_index = self.size
        node.id = new_index
        node.left = -1
        node.right = -1
        node.height = 1
        self._write_node(new_index, node)

        if self.root_ptr == -1:
            self.root_ptr = new_index
            self.size = 1
            self._write_header(self.size, self.root_ptr)
            return new_index

        self.root_ptr = self._insert_recursive(self.root_ptr, new_index)
        self.size += 1
        self._write_header(self.size, self.root_ptr)
        return new_index

    def search(self, id_key: int) -> Optional[Node]:
        """Busca un nodo por id_key y devuelve el Node si existe, sino None."""
        current_idx = self.root_ptr
        while current_idx != -1:
            node = self._read_node(current_idx)
            if id_key == node.Employee_ID:
                return node
            elif id_key < node.Employee_ID:
                current_idx = node.left
            else:
                current_idx = node.right
        return None

    def _delete_recursive(self, current_idx: int, id_key: int) -> Tuple[int, bool]:
        if current_idx == -1:
            return -1, False

        node = self._read_node(current_idx)
        deleted = False

        if id_key < node.Employee_ID:
            node.left, deleted = self._delete_recursive(node.left, id_key)
        elif id_key > node.Employee_ID:
            node.right, deleted = self._delete_recursive(node.right, id_key)
        else:
            deleted = True
            if node.left == -1:
                return node.right, True
            elif node.right == -1:
                return node.left, True

            temp_idx = node.right
            while True:
                temp_node = self._read_node(temp_idx)
                if temp_node.left == -1:
                    break
                temp_idx = temp_node.left

            successor = self._read_node(temp_idx)
            node.Employee_ID = successor.Employee_ID
            node.Employee_Name = successor.Employee_Name
            node.Age = successor.Age
            node.Country = successor.Country
            node.Department = successor.Department
            node.Position = successor.Position
            node.Salary = successor.Salary
            node.Joining_Date = successor.Joining_Date
            node.right, _ = self._delete_recursive(node.right, successor.Employee_ID)

        self._write_node(current_idx, node)
        self._update_height(current_idx)
        balance = self._get_balance(current_idx)

        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(current_idx), deleted

        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._rotate_left(node.left)
            self._write_node(current_idx, node)
            return self._rotate_right(current_idx), deleted

        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(current_idx), deleted

        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._rotate_right(node.right)
            self._write_node(current_idx, node)
            return self._rotate_left(current_idx), deleted

        return current_idx, deleted

    def delete(self, id_key: int) -> bool:
        """Elimina el nodo con id_key.

        Debe soportar los casos clásicos de borrado en BST (hoja, un hijo, dos hijos),
        actualizando los punteros persistidos y la cabecera si corresponde.

        Retorna True si se eliminó, False si no existía.
        """
        if self.root_ptr == -1:
            return False
        self.root_ptr, deleted = self._delete_recursive(self.root_ptr, id_key)
        if not deleted:
            return False
        self.size -= 1
        self._write_header(self.size, self.root_ptr)
        return True
       

    def _range_search_recursive(self, current_idx: int, low: int, high: int, results: List[Node]) -> None:
        if current_idx == -1:
            return
        node = self.get_node(current_idx)
        if low < node.Employee_ID:
            self._range_search_recursive(node.left, low, high, results)
        if low <= node.Employee_ID <= high:
            results.append(node)
        if high > node.Employee_ID:
            self._range_search_recursive(node.right, low, high, results)

    def range_search(self, low_id: int, high_id: int) -> List[Node]:
        """Devuelve la lista de nodos con id en el rango [low_id, high_id]."""
        results = []
        self._range_search_recursive(self.root_ptr, low_id, high_id, results)
        return results

    def load_from_csv(self, csv_filename: str, max_records: Optional[int] = None) -> int:
        """Carga registros desde un archivo CSV y los inserta en el árbol."""
        count = 0
        with open(csv_filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                if max_records is not None and count >= max_records:
                    break
                node = Node(
                    Employee_ID=int(row['Employee_ID']),
                    Employee_Name=row['Employee_Name'],
                    Age=int(row['Age']),
                    Country=row['Country'],
                    Department=row['Department'],
                    Position=row['Position'],
                    Salary=float(row['Salary']),
                    Joining_Date=row['Joining_Date']
                )
                inserted = self.insert(node)
                if inserted != -1:
                    count += 1
        return count

    def close(self) -> None:
        """Cierra el archivo subyacente y asegura que la cabecera esté actualizada."""
        return self.file.close()


def print_node(node: Node) -> None:
    if node is None:
        print("No encontrado")
        return
    print(
        f"ID={node.Employee_ID}, Name={node.Employee_Name}, Age={node.Age}, "
        f"Country={node.Country}, Dept={node.Department}, Pos={node.Position}, "
        f"Salary={node.Salary:.2f}, Date={node.Joining_Date}, Height={node.height}"
    )


def main() -> None:
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.abspath(os.path.join(base_dir, '..', 'employee.csv'))
    bin_path = os.path.join(base_dir, 'avl_employees.bin')

    if os.path.exists(bin_path):
        os.remove(bin_path)

    tree = BSTFile(bin_path)

    print('Cargando registros desde CSV...')
    loaded = tree.load_from_csv(csv_path, max_records=200)
    print(f'Registros cargados: {loaded}')
    print(f'Root pointer: {tree.root_ptr}, size: {tree.size}')

    search_id = 17648
    print(f'Buscando empleado con ID {search_id}...')
    print_node(tree.search(search_id))

    new_employee = Node(
        Employee_ID=999999,
        Employee_Name='Nuevo Empleado',
        Age=30,
        Country='Peru',
        Department='IT',
        Position='Developer',
        Salary=12345.67,
        Joining_Date='01/01/2026',
    )
    inserted_index = tree.insert(new_employee)
    print(f'Insertando nuevo empleado con ID {new_employee.Employee_ID}, indice={inserted_index}')
    print_node(tree.search(new_employee.Employee_ID))

    delete_id = search_id
    deleted = tree.delete(delete_id)
    print(f'Eliminando empleado ID {delete_id}:', 'OK' if deleted else 'No existe')
    print('Verificando eliminación...')
    print_node(tree.search(delete_id))

    print('Búsqueda por rango entre 5000 y 20000...')
    results = tree.range_search(5000, 20000)
    print(f'Total encontrados: {len(results)}')
    for node in results[:10]:
        print_node(node)

    tree.close()


if __name__ == '__main__':
    main()
