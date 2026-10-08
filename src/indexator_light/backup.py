"""Сравнение исходной папки с резервной копией (по относительным путям)."""
from duplicates import file_hash


def compare_with_backup(source_files, backup_files):
    """Возвращает словарь со списками относительных путей:
    missing - есть в источнике, нет в бэкапе;
    changed - есть в обоих, но содержимое различается;
    extra   - есть в бэкапе, нет в источнике.
    """
    src = {f.rel_path: f for f in source_files}
    bak = {f.rel_path: f for f in backup_files}

    missing = sorted(set(src) - set(bak))
    extra = sorted(set(bak) - set(src))
    changed = []
    errors = []
    for rel in sorted(set(src) & set(bak)):
        s, b = src[rel], bak[rel]
        if s.size != b.size:
            changed.append(rel) 
        try:
            if file_hash(s.path) != file_hash(b.path):
                changed.append(rel)
        except OSError as e:
            errors.append((rel, str(e)))
    return {"missing": missing, "changed": changed, "extra": extra}, errors
