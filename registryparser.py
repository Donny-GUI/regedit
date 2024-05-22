from multiprocessing import Pool, freeze_support
from typing import List, Dict
import re
from dataclasses import dataclass


binarypat = re.compile(
    r'^(?P<address>[0-9a-fA-F]+)\s+'                    # Address (hexadecimal)
    r'(?P<bytes1>(?:[0-9a-fA-F]{2}\s?){8})\s*-\s*'       # First group of bytes
    r'(?P<bytes2>(?:[0-9a-fA-F]{2}\s?){8})\s+'           # Second group of bytes
    r'(?P<ascii>.*)$'                                    # ASCII representation
)

@dataclass
class BinaryAddress:
    address: str 
    bytes1 : str
    bytes2 : str
    ascii  : str

    def list(self):
        return [self.address, self.bytes1, self.bytes2, self.ascii]

    def string(self):
        return "\t".join(self.list())


BinaryData = List[BinaryAddress]
Values = List[Dict[str,str]]
Entry = Dict[str, str|Values]
RegistryEntries = List[Entry]


def vsplit(string: str):
    return string.split(" ")[1].strip()

def kvsplit(string: str):
    try:
        return string.split(":", 1)[1].strip()
    except:
        return string

def reg_binary_part(liter: iter):
    d = []
    while True: 
        try:
            x = next(liter)
        except StopIteration:
            break
        if x != "":
            d.append(x)
    return "\n".join(d)


def collect_values(line: str, liter: iter):
    values = []
    value = {}
    value["index"] = vsplit(line)
    while True:
        try:
            nextvalue: str = next(liter)
        except StopIteration:
            break
        if nextvalue == "":
            continue
        elif nextvalue.startswith("Value "):
            value["index"] = vsplit(line)
            continue

        nv = nextvalue.strip()
        if nv.startswith("Name:"):
            value["name"] = kvsplit(nv)
        elif nv.startswith("Type:"):
            value["type"] = kvsplit(nv)
        elif nv.startswith("Data:"):
            if value["type"] == "REG_BINARY":
                value["data"] = reg_binary_part(liter)
            else:
                value["data"] = kvsplit(nv)
            values.append(value)
            value = {}
    return values

def parse_section(section: str) -> RegistryEntries:
    lines = section.split("\n")
    n = lines.pop(0)
    liter = iter(lines)
    retv = {"key":kvsplit(n), "values":[]}

    while True:
        try:
            line = next(liter)
        except StopIteration:
            break
        if line.startswith("Key Name:"):
            retv["key"] = kvsplit(line)
            continue
        elif line.startswith("Class Name:"):
            retv["class"] = kvsplit(line)
            continue
        elif line.startswith("Last Write Time:"):
            datetime = kvsplit(line)
            dt = datetime.split("-", 1)
            retv["date"] = dt[0] 
            try:
                retv["time"] = dt[1]
            except:
                retv["time"] = ""
            continue 
        elif line.startswith("Value "):
            retv["values"] = collect_values(line, liter)
                   
    return retv


def parse_registry_file(file_path: str):
    with open(file_path, 'r', encoding="utf-16", errors="ignore") as file:
        content = str(file.read())
    sections = content.split("Key Name:")
    with Pool(processes=4) as pool:
        results = pool.map(parse_section, sections)
    return results
    

if __name__ == '__main__':
    from pprint import pprint
    freeze_support()
    file_path = 'reg.txt'
    parsed_data = parse_registry_file(file_path)
    print("finished")
    for entry in parsed_data[:150]:
        pprint(entry)