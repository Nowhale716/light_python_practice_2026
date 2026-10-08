"""Поиск дубликатов: хэш -> список путей (только в памяти)."""
import hashlib

""" Получение отпечатка содержимого файла"""
def file_hash(path, chunk_size=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(files):
    """Возвращает (группы, ошибки).

    группы: {хэш: [пути]} только для групп из 2+ файлов.
    Оптимизация: сначала группируем по размеру, хэш считаем лишь для
    файлов, у которых есть «ровесник» по размеру.
    """
    by_size = {}
    for f in files:
        by_size.setdefault(f.size, []).append(f)

    by_hash = {}
    errors = []
    for same_size in by_size.values():
        if len(same_size) < 2:
            continue
        for f in same_size:
            try:
                by_hash.setdefault(file_hash(f.path), []).append(f.path)
            except OSError as e:
                errors.append((f.path, str(e)))

    groups = {h: sorted(p) for h, p in by_hash.items() if len(p) >= 2}
    return groups, errors
