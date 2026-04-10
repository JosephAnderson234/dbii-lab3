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
import os


@dataclass
class Record:
    id: int
    name: str
    age: int
    country: str
    department: str
    position: str
    salary: float
    join_date: str

class SequentialFile:
    
    HEADER_FORMAT = 'ii'
    RECORD_FORMAT = 'i30si20s20s20sf10s?' #TODO: definir el formato de struct para el nodo

    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    RECORD_SIZE = struct.calcsize(RECORD_FORMAT)
    
    

    def __init__(self, filename: str, k_threshold: int = 100):
        """Inicializa SequentialFile sobre filename.

        - k_threshold es el umbral de tamaño del área auxiliar que provoca la reconstrucción.
        - Debe abrir/crear el archivo en modo binario lectura/escritura.
        - Si el archivo es nuevo, inicializar la cabecera con ordered_count=0 y aux_count=0.
        
        - k == log2(n) es un buen punto de partida para el umbral, pero puede ajustarse según pruebas de rendimiento.
        """
        if (not os.path.exists(filename)):
            with open(filename, 'wb') as f:
                self.ordered_count = 0
                self.aux_count = 0
                f.write(struct.pack(self.HEADER_FORMAT, 0, 0))  # ordered_count=0, aux_count=0
        self.file = open(filename, 'r+b')
        self.k_threshold = k_threshold 

        _ordered_count, _aux_count = self._read_header()
        self.ordered_count = _ordered_count
        self.aux_count = _aux_count

    def _read_header(self) -> Tuple[int, int]:
        """Lee y devuelve (ordered_count, aux_count) desde la cabecera."""
        self.file.seek(0)
        data = self.file.read(self.HEADER_SIZE)
        return struct.unpack(self.HEADER_FORMAT, data)

    def _write_header(self, ordered_count: int, aux_count: int) -> None:
        self.file.seek(0)
        self.file.write(struct.pack(self.HEADER_FORMAT, ordered_count, aux_count))
        self.file.flush()

    def _pack_record(self, rec: Record, flag: bool) -> bytes:
        """Empaqueta un Record en bytes según RECORD_FORMAT."""
        name_bytes = rec.name.encode('utf-8')[:30].ljust(30, b'\x00')
        country_bytes = rec.country.encode('utf-8')[:20].ljust(20, b'\x00')
        department_bytes = rec.department.encode('utf-8')[:20].ljust(20, b'\x00')
        position_bytes = rec.position.encode('utf-8')[:20].ljust(20, b'\x00')
        join_date_bytes = rec.join_date.encode('utf-8')[:10].ljust(10, b'\x00')
        
        return struct.pack(self.RECORD_FORMAT, rec.id, name_bytes, rec.age, country_bytes, department_bytes, position_bytes, rec.salary, join_date_bytes, flag) #TODO: el último campo es para el flag de eliminado, ajustar según diseño

    def _unpack_record(self, data: bytes) -> Tuple[Record, bool]:
        id, name, age, country, department, position, salary, join_date, is_deleted = struct.unpack(self.RECORD_FORMAT, data)
        return Record(
            id=id,
            name=name.decode('utf-8').rstrip('\x00'),
            age=age,
            country=country.decode('utf-8').rstrip('\x00'),
            department=department.decode('utf-8').rstrip('\x00'),
            position=position.decode('utf-8').rstrip('\x00'),
            salary=salary,
            join_date=join_date.decode('utf-8').rstrip('\x00')
        ), is_deleted

    def binary_search(self, id_key: int) -> Optional[Record]:
        """Realiza búsqueda binaria sobre la parte ordenada por id_key. """
        if (self.ordered_count == 0):
            return None
        
        low, high = 0, self.ordered_count - 1
        while low <= high:
            mid = (low + high) // 2
            self.file.seek(self.HEADER_SIZE + mid * self.RECORD_SIZE)
            data = self.file.read(self.RECORD_SIZE)
            rec, is_deleted = self._unpack_record(data)
            
            if rec.id == id_key and not is_deleted:
                return rec 
            elif rec.id < id_key:
                low = mid + 1
            else:
                high = mid - 1
        return None
        
        
    def search(self, id_key: int) -> Optional[Record]:
        """Busca id_key en todo el archivo (ordenado + área auxiliar). """
        rec = self.binary_search(id_key)
        if rec is not None:
            return rec
        
        for i in range(self.aux_count):
            self.file.seek(self.HEADER_SIZE + (self.ordered_count + i) * self.RECORD_SIZE)
            data = self.file.read(self.RECORD_SIZE)
            rec, is_deleted = self._unpack_record(data)
            if rec.id == id_key and not is_deleted:
                return rec
        return None

    def insert(self, rec: Record) -> int:
        """Inserta rec en el área auxiliar (al final del archivo).
        
        - Incrementa aux_count en la cabecera.
        - Si aux_count supera k_threshold, llama a _rebuild() para mezclar y ordenar.
        """
        if self.search(rec.id) is not None:
            raise ValueError(f"Registro con id {rec.id} ya existe.")
        
        self.file.seek(self.HEADER_SIZE + (self.ordered_count + self.aux_count)*self.RECORD_SIZE)
        self.file.write(self._pack_record(rec, False))
        self.aux_count += 1
        self._write_header(self.ordered_count, self.aux_count)
        
        if self.aux_count > self.k_threshold:
            self._rebuild()
        return rec.id

    def delete(self, id_key: int) -> bool:
        """Elimina el registro con id_key. """
        """
        Procurar hacer un recorrido similar a busqueda binaria para encontrar el registro a eliminar, y marcarlo como eliminado (sin remover físicamente del archivo).
        O hacerlo linealmente en la parte auxiliar, y luego marcarlo como eliminado. La estrategia de punteros puede ayudar a gestionar los eliminados sin necesidad de reconstruir inmediatamente.
        """
        if self.search(id_key) is None:
            return False
        
        if self.ordered_count > 0:
            low, high = 0, self.ordered_count - 1
            while low <= high:
                mid = (low + high) // 2
                self.file.seek(self.HEADER_SIZE + mid * self.RECORD_SIZE)
                data = self.file.read(self.RECORD_SIZE)
                rec, is_deleted = self._unpack_record(data)
                
                if rec.id == id_key and not is_deleted:
                    self.file.seek(self.HEADER_SIZE + mid * self.RECORD_SIZE + self.RECORD_SIZE - 1) #TODO: ajustar según diseño del flag
                    self.file.write(struct.pack('?', True)) #marcar como eliminado
                    self.file.flush()
                    return True
                elif rec.id < id_key:
                    low = mid + 1
                else:
                    high = mid - 1
        
        ## Hatsa este punto se hizo la búsqueda binaria en la parte ordenada, ahora se hace la búsqueda lineal en el área auxiliar
        for i in range(self.aux_count):
            self.file.seek(self.HEADER_SIZE + (self.ordered_count + i) * self.RECORD_SIZE)
            data = self.file.read(self.RECORD_SIZE)
            rec, is_deleted = self._unpack_record(data)
            if rec.id == id_key and not is_deleted:
                self.file.seek(self.HEADER_SIZE + (self.ordered_count + i) * self.RECORD_SIZE + self.RECORD_SIZE - 1) #TODO: ajustar según diseño del flag
                self.file.write(struct.pack('?', True)) #marcar como eliminado
                self.file.flush()
        return True
        

    def _rebuild(self) -> None:
        """Reconstruye el archivo mezclando la parte ordenada con el área auxiliar
        y escribiendo un único bloque ordenado. """
        ordered_counter, aux_counter = self._read_header()
        self.file.seek(self.HEADER_SIZE)
        data = self.file.read((ordered_counter + aux_counter) * self.RECORD_SIZE)
        
        records = [self._unpack_record(data[i:i+self.RECORD_SIZE])
                   for i in range(0, len(data), self.RECORD_SIZE)]
        records = [rec for rec, is_deleted in records if not is_deleted]
        records.sort(key=lambda r: r.id)
        
        self.file.seek(0)
        self._write_header(len(records), 0)
        for rec in records:
            self.file.write(self._pack_record(rec, False))
        self.file.flush()

    def range_search(self, id_min: int, id_max: int) -> List[Record]:
        """Devuelve una lista de registros con id en el rango [id_min, id_max]."""
        results = []
        for i in range(self.ordered_count):
            self.file.seek(self.HEADER_SIZE + i * self.RECORD_SIZE)
            data = self.file.read(self.RECORD_SIZE)
            rec, is_deleted = self._unpack_record(data)
            if not is_deleted and id_min <= rec.id <= id_max:
                results.append(rec)
        
        for i in range(self.aux_count):
            self.file.seek(self.HEADER_SIZE + (self.ordered_count + i) * self.RECORD_SIZE)
            data = self.file.read(self.RECORD_SIZE)
            rec, is_deleted = self._unpack_record(data)
            if not is_deleted and id_min <= rec.id <= id_max:
                results.append(rec)
        
        return results

    def close(self) -> None:
        """Cierra el archivo subyacente asegurando que la cabecera esté persistida."""
        self.file.flush()
        self.file.close()