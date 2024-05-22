import winreg as wr
import os
from enum import Enum

class Dir(Enum):
    ENV = "Environment"
    NETWORK = "Network"

class Key(Enum):
    PATH = "PATH"

class Variables(Enum):
    PATH = [Dir.ENV, Key.PATH]


def set_keyvalue(registry_directory:str, keyname:str, keyvalue:str):
    with wr.CreateKey(wr.HKEY_CURRENT_USER, registry_directory) as _:
        with wr.OpenKey(wr.HKEY_CURRENT_USER, registry_directory, 0, wr.KEY_WRITE) as write_registry_dir:
            wr.SetValueEx(write_registry_dir, keyname, 0, wr.REG_SZ, keyvalue)


def get_keyvalue(registry_directory:str, keyname:str) -> str:
    with wr.OpenKey(wr.HKEY_CURRENT_USER, registry_directory) as access_registry_dir:
        value, _ = wr.QueryValueEx(access_registry_dir, keyname)
        return value





def get_path() -> list[str]:
    return get_keyvalue(*Variables.PATH).split(";")
    
def append_to_path(directory: str) -> None:
    values = get_path()
    if directory in values:
        return
    values.append(directory)
    value = ";".join(values)
    set_keyvalue(Dir.ENV, Key.PATH, value)

def new_environment_variable(name: str, value:str):
    set_keyvalue(Dir.ENV, name, value)
    