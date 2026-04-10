"""Archivo secuencial con área auxiliar.

- Cabecera: struct 'ii' -> (ordered_count, aux_count)
  - ordered_count: número de registros en la parte ordenada inicial
  - aux_count: número de registros en el área auxiliar (insertados al final)

Los registros están ordenados por id en la parte ordenada. Los nuevos
registros se agregan al final del archivo (área auxiliar). Cuando aux_count
supera un umbral k, se debe reconstruir el archivo mezclando la parte ordenada
con los registros auxiliares para producir un único archivo ordenado.

Opcionalmente, puede implementar la estrategia de punteros para gestionar mejor los eliminados.
"""
from dataclasses import dataclass
from typing import Optional, List, Tuple
import struct
import io


@dataclass
class Record:
    id: int
    name: str
    age: int
    country: str


class SequentialFile:
    
    HEADER_FORMAT = 'ii'
    RECORD_FORMAT = '' #TODO: definir el formato de struct para el nodo 

    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    RECORD_SIZE = struct.calcsize(RECORD_FORMAT)

    def __init__(self, filename: str, k_threshold: int = 100):
        """Inicializa SequentialFile sobre filename.

        - k_threshold es el umbral de tamaño del área auxiliar que provoca la reconstrucción.
        - Debe abrir/crear el archivo en modo binario lectura/escritura.
        - Si el archivo es nuevo, inicializar la cabecera con ordered_count=0 y aux_count=0.
        """
        raise NotImplementedError()

    def _read_header(self) -> Tuple[int, int]:
        """Lee y devuelve (ordered_count, aux_count) desde la cabecera."""
        raise NotImplementedError()

    def _write_header(self, ordered_count: int, aux_count: int) -> None:
        """Escribe la cabecera con (ordered_count, aux_count)."""
        raise NotImplementedError()

    def _pack_record(self, rec: Record) -> bytes:
        """Empaqueta un Record en bytes según RECORD_FORMAT."""
        raise NotImplementedError()

    def _unpack_record(self, data: bytes) -> Record:
        """Desempaqueta bytes en una instancia de Record."""
        raise NotImplementedError()

    def binary_search(self, id_key: int) -> Optional[Record]:
        """Realiza búsqueda binaria sobre la parte ordenada por id_key. """
        raise NotImplementedError()

    def search(self, id_key: int) -> Optional[Record]:
        """Busca id_key en todo el archivo (ordenado + área auxiliar). """
        raise NotImplementedError()

    def insert(self, rec: Record) -> int:
        """Inserta rec en el área auxiliar (al final del archivo).

        - Incrementa aux_count en la cabecera.
        - Si aux_count supera k_threshold, llama a _rebuild() para mezclar y ordenar.
        """
        raise NotImplementedError()

    def delete(self, id_key: int) -> bool:
        """Elimina el registro con id_key. """
        raise NotImplementedError()

    def _rebuild(self) -> None:
        """Reconstruye el archivo mezclando la parte ordenada con el área auxiliar
        y escribiendo un único bloque ordenado. """
        raise NotImplementedError()

    def close(self) -> None:
        """Cierra el archivo subyacente asegurando que la cabecera esté persistida."""
        raise NotImplementedError()
