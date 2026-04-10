from typing import List, Tuple, Optional
from dataclasses import dataclass
from sequential import SequentialFile, Record

csv_data = open("employee.csv", "r").readlines()

## For each line in the csv, parse it and create a Record object, then insert it into the sequential file

def parse_csv_line(line: str) -> Record:
    fields = line.strip().split(";")
    return Record(
        id=int(fields[0]),
        name=fields[1],
        age=int(fields[2]),
        country=fields[3],
        department=fields[4],
        position=fields[5],
        salary=float(fields[6]),
        join_date=fields[7]
    )
    
    
def import_csv_to_sequential(filename: str, csv_lines: List[str]) -> None:
    ## igonore the first line of the csv, which contains the headers
    csv_lines = csv_lines[1:]
    seq_file = SequentialFile(filename, k_threshold=100)
    for line in csv_lines:
        rec = parse_csv_line(line)
        seq_file.insert(rec)
    
if __name__ == "__main__":
    import_csv_to_sequential("employees.dat", csv_data)