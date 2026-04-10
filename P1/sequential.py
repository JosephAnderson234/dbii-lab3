"""Archivo secuencial con área auxiliar.
- Cabecera: struct 'ii' -> (ordered_count, aux_count)
- ordered_count: número de registros en la parte ordenada inicial
- aux_count: número de registros en el área auxiliar (insertados al final)
Los registros están ordenados por id en la parte ordenada. Los nuevos
registros se agregan al final del archivo (área auxiliar). Cuando aux_count
supera un umbral k, se debe reconstruir el archivo mezclando la parte ordenada
con los registros auxiliares para producir un único archivo ordenado.
Opcionalmente, puede implementar la estrategia de punteros para gestionar mejor los
eliminados.
"""
import struct
import os
import math
from dataclasses import dataclass
from typing import Optional, List, Tuple

@dataclass
class Record:
    id: int
    name: str
    age: int
    country: str
    department: str
    position: str
    salary: float
    joining_date: str

class SequentialFile:
    # i: id(4), 30s: name(30), i: age(4), 20s: country(20), 
    # 20s: dept(20), 20s: pos(20), f: salary(4), 10s: date(10), ?: del_flag(1)
    HEADER_FORMAT = 'ii'
    RECORD_FORMAT = 'i30si20s20s20sf10s?' 

    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    RECORD_SIZE = struct.calcsize(RECORD_FORMAT)

    def __init__(self, filename: str):
        self.filename = filename
        
        if not os.path.exists(self.filename):
            with open(self.filename, 'wb') as f:
                f.write(struct.pack(self.HEADER_FORMAT, 0, 0))
        
        self.file = open(self.filename, 'r+b')

    def _read_header(self) -> Tuple[int, int]:
        self.file.seek(0)
        data = self.file.read(self.HEADER_SIZE)
        return struct.unpack(self.HEADER_FORMAT, data)

    def _write_header(self, ordered_count: int, aux_count: int) -> None:
        self.file.seek(0)
        self.file.write(struct.pack(self.HEADER_FORMAT, ordered_count, aux_count))

    def _pack_record(self, rec: Record, is_deleted: bool = False) -> bytes:
        return struct.pack(
            self.RECORD_FORMAT,
            rec.id,
            rec.name.encode('utf-8')[:30].ljust(30, b'\0'),
            rec.age,
            rec.country.encode('utf-8')[:20].ljust(20, b'\0'),
            rec.department.encode('utf-8')[:20].ljust(20, b'\0'),
            rec.position.encode('utf-8')[:20].ljust(20, b'\0'),
            rec.salary,
            rec.joining_date.encode('utf-8')[:10].ljust(10, b'\0'),
            is_deleted
        )

    def _unpack_record(self, data: bytes) -> Tuple[Record, bool]:
        unp = struct.unpack(self.RECORD_FORMAT, data)
        rec = Record(
            id=unp[0],
            name=unp[1].decode('utf-8').strip('\x00'),
            age=unp[2],
            country=unp[3].decode('utf-8').strip('\x00'),
            department=unp[4].decode('utf-8').strip('\x00'),
            position=unp[5].decode('utf-8').strip('\x00'),
            salary=unp[6],
            joining_date=unp[7].decode('utf-8').strip('\x00')
        )
        return rec, unp[8]

    def binary_search(self, id_key: int) -> Optional[Record]:
        """Búsqueda binaria en la sección físicamente ordenada: O(log n)"""
        ordered_count, _ = self._read_header()
        low = 0
        high = ordered_count - 1
        
        while low <= high:
            mid = (low + high) // 2
            self.file.seek(self.HEADER_SIZE + mid * self.RECORD_SIZE)
            rec, deleted = self._unpack_record(self.file.read(self.RECORD_SIZE))
            
            if rec.id == id_key:
                return rec if not deleted else None
            elif rec.id < id_key:
                low = mid + 1
            else:
                high = mid - 1
        return None

    def search(self, id_key: int) -> Optional[Record]:
        """Búsqueda híbrida: O(log n) + O(k)"""
        # 1. Búsqueda binaria en parte principal
        res = self.binary_search(id_key)
        if res: return res
        
        # 2. Búsqueda lineal en área auxiliar
        ord_c, aux_c = self._read_header()
        self.file.seek(self.HEADER_SIZE + ord_c * self.RECORD_SIZE)
        for _ in range(aux_c):
            rec, deleted = self._unpack_record(self.file.read(self.RECORD_SIZE))
            if rec.id == id_key and not deleted:
                return rec
        return None

    def insert(self, rec: Record) -> bool:
        """Inserción con validación de unicidad y k dinámico: O(search) + O(1)"""
        
        if self.search(rec.id):
            print(f"Error: El ID {rec.id} ya existe.")
            return False

        ord_c, aux_c = self._read_header()
        
        
        self.file.seek(0, os.SEEK_END)
        self.file.write(self._pack_record(rec))
        
        aux_c += 1
        self._write_header(ord_c, aux_c)
        
        # k = log2(n)
        n_total = ord_c + aux_c
        dynamic_k = max(10, math.ceil(math.log2(n_total)))
        
        if aux_c >= dynamic_k:
            print(f"Rebuild disparado (k={dynamic_k})...")
            self._rebuild()
        
        return True

    def delete(self, id_key: int) -> bool:
        """Eliminación lógica optimizada: O(log n) + O(k)"""
        ord_c, aux_c = self._read_header()
  
        low = 0
        high = ord_c - 1
        while low <= high:
            mid = (low + high) // 2
            pos = self.HEADER_SIZE + mid * self.RECORD_SIZE
            self.file.seek(pos)
            
            rec, deleted = self._unpack_record(self.file.read(self.RECORD_SIZE))
            
            if rec.id == id_key:
                if not deleted:
                 
                    self.file.seek(pos)
                    self.file.write(self._pack_record(rec, is_deleted=True))
                    return True
                return False 
            elif rec.id < id_key:
                low = mid + 1
            else:
                high = mid - 1

        
        self.file.seek(self.HEADER_SIZE + ord_c * self.RECORD_SIZE)
        for i in range(aux_c):
            pos = self.file.tell() 
            rec, deleted = self._unpack_record(self.file.read(self.RECORD_SIZE))
            
            if rec.id == id_key and not deleted:
                
                self.file.seek(pos)
                self.file.write(self._pack_record(rec, is_deleted=True))
                return True
                
        return False # No existe en ninguna parte

    def range_search(self, init_key: int, end_key: int) -> List[Record]:
        """Búsqueda por rango optimizada."""
        ord_c, aux_c = self._read_header()
        results = []
       
        self.file.seek(self.HEADER_SIZE)
        for _ in range(ord_c + aux_c):
            rec, deleted = self._unpack_record(self.file.read(self.RECORD_SIZE))
            if not deleted and init_key <= rec.id <= end_key:
                results.append(rec)
        
        results.sort(key=lambda x: x.id)
        return results

    def _rebuild(self) -> None:
        """Mezcla y reordenamiento físico: O(n + k)"""
        ord_c, aux_c = self._read_header()
        all_records = []
  
        self.file.seek(self.HEADER_SIZE)
        for _ in range(ord_c + aux_c):
            data = self.file.read(self.RECORD_SIZE)
            rec, deleted = self._unpack_record(data)
            if not deleted:
                all_records.append(rec)
  
        all_records.sort(key=lambda x: x.id)
        
        self.file.seek(self.HEADER_SIZE)
        for r in all_records:
            self.file.write(self._pack_record(r))
        
        self.file.truncate(self.HEADER_SIZE + len(all_records) * self.RECORD_SIZE)
        self._write_header(len(all_records), 0)

    def close(self) -> None:
        if self.file:
            self.file.close()