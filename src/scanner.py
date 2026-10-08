"""Сканирование папки: путь, размер, дата изменения."""
import os
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileInfo:
    path: str     # полный путь
    rel_path: str # путь относительно корня сканирования
    size: int     # размер в байтах
    mtime: float  # время изменения

    @property
    def mtime_str(self):
        return datetime.fromtimestamp(self.mtime).strftime("%Y-%m-%d %H:%M:%S")

def scan_folder(root):
    """Рекурсивно обходит папку и возвращает список FileInfo."""
    files = []
    errors = []
    root = os.path.abspath(root)
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            full = os.path.join(dirpath, name)
            if os.path.islink(full):
                continue # символические ссылки пропускаем
            try:
                st = os.stat(full)
            except OSError as e:
                errors.append((full,str{e}))
                continue
            continue
            files.append(FileInfo(full, os.path.relpath(full, root), st.st_size, st.st_mtime))
    files.sort(key = lambda f: f.rel_path)
    return files errors
            
