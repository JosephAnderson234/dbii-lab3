"""BST persistido en archivo binario.

El archivo comienza con una cabecera que contiene:
- size (int): número total de registros
- root_ptr (int): índice del nodo raíz (-1 si vacío)
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
import struct

@dataclass
class Node:
    # TODO: definir los campos del nodo
    id: int = 0
    left: int = -1
    right: int = -1


class BSTFile:
    HEADER_FORMAT = 'ii'
    NODE_FORMAT = '' #TODO: definir el formato de struct para el nodo 

    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    NODE_SIZE = struct.calcsize(NODE_FORMAT)

    def __init__(self, filename: str):
        """Inicializa la instancia sobre filename.

        - Debe abrir/crear el archivo en modo binario lectura/escritura.
        - Si el archivo es nuevo, debe inicializar la cabecera con size=0 y root_ptr=-1.
        """
        raise NotImplementedError()

    def _read_header(self) -> Tuple[int, int]:
        """Lee y devuelve (size, root_ptr) desde la cabecera del archivo."""
        raise NotImplementedError()

    def _write_header(self, size: int, root_ptr: int) -> None:
        """Escribe la cabecera (size, root_ptr) en el archivo."""
        raise NotImplementedError()

    def _node_offset(self, index: int) -> int:
        """Calcula el offset byte donde se almacena el nodo index en el archivo.

        Se asume una asignación por índice (por ejemplo, el primer nodo tiene index 0,
        y su offset es HEADER_SIZE + 0 * NODE_SIZE).
        """
        raise NotImplementedError()

    def _pack_node(self, node: Node) -> bytes:
        """Empaqueta un Node en bytes según NODE_FORMAT."""
        raise NotImplementedError()

    def _unpack_node(self, data: bytes) -> Node:
        """Desempaqueta bytes en una instancia de Node."""
        raise NotImplementedError()

    def insert(self, node: Node) -> int:
        """Inserta node en el árbol persistente.

        Debe:
        - Escribir el nodo al final (o en una posición libre según diseño).
        - Actualizar punteros left/right de los nodos padre según correspondan.
        - Actualizar la cabecera size y, si corresponde, root_ptr.

        Retorna el índice (o puntero) donde se almacenó el nodo.
        """
        raise NotImplementedError()

    def search(self, id_key: int) -> Optional[Node]:
        """Busca un nodo por id_key y devuelve el Node si existe, sino None."""
        raise NotImplementedError()

    def delete(self, id_key: int) -> bool:
        """Elimina el nodo con id_key.

        Debe soportar los casos clásicos de borrado en BST (hoja, un hijo, dos hijos),
        actualizando los punteros persistidos y la cabecera si corresponde.

        Retorna True si se eliminó, False si no existía.
        """
        raise NotImplementedError()

    def range_search(self, low_id: int, high_id: int) -> List[Node]:
        """Devuelve la lista de nodos con id en el rango [low_id, high_id]."""
        raise NotImplementedError()

    def close(self) -> None:
        """Cierra el archivo subyacente y asegura que la cabecera esté actualizada."""
        raise NotImplementedError()
