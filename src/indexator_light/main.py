"""Консольный индексатор папок.

Примеры:
    python src/main.py ./photos
    python src/main.py ./photos --backup ./photos_backup
    python src/main.py ./photos --backup ./backup --report report.txt
"""

import argparse
import os
import sys

from scanner import scan_folder
from duplicates import find_duplicates
from backup import compare_with_backup


def human_size(n):
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if n < 1024 or unit == "ГБ":
            return f"{n:.0f} {unit}" if unit == "Б" else f"{n:.1f} {unit}"
        n /= 1024


def parse_args():
    p = argparse.ArgumentParser(description="Индексатор папок: метаданные, дубликаты, сравнение с бэкапом")
    p.add_argument("path", help="путь к папке для индексации")
    p.add_argument("--backup", metavar="PATH", help="путь к резервной копии для сравнения")
    p.add_argument("--report", metavar="FILE", help="сохранить отчет в текстовый файл")
    return p.parse_args()


def check_dir(path, label):
    if not os.path.isdir(path):
        print(f"Ошибка: {label} '{path}' не существует или не является папкой.", file=sys.stderr)
        sys.exit(1)


def main():
    args = parse_args()
    check_dir(args.path, "папка")
    if args.backup:
        check_dir(args.backup, "папка резервной копии")

    lines = []  # короткий отчет собираем в список

    # --- Этап 2: сканирование ---
    files, scan_errors = scan_folder(args.path)
    total = sum(f.size for f in files)
    print(f"Файлы в '{args.path}':")
    for f in files:
        print(f"  {f.rel_path} | {human_size(f.size)} | {f.mtime_str}")
    lines.append(f"Папка: {os.path.abspath(args.path)}")
    lines.append(f"Файлов: {len(files)}, общий размер: {human_size(total)}")

    # --- Этап 3: дубликаты ---
    groups, hash_errors = find_duplicates(files)
    print("\nДубликаты:")
    if not groups:
        print("  не найдены")
    for i, (h, paths) in enumerate(groups.items(), 1):
        print(f"  Группа {i} (sha256 {h[:12]}...):")
        for p in paths:
            print(f"    {os.path.relpath(p, args.path)}")
    lines.append(f"Групп дубликатов: {len(groups)}")

    # --- Этап 4: бэкап ---
    backup_errors = []
    if args.backup:
        backup_files, e1 = scan_folder(args.backup)
        diff, e2 = compare_with_backup(files, backup_files)
        backup_errors = e1 + e2
        print(f"\nСравнение с резервной копией '{args.backup}':")
        for key, title in (("missing", "Отсутствуют в бэкапе"),
                           ("changed", "Изменены"),
                           ("extra", "Лишние в бэкапе")):
            print(f"  {title}: {len(diff[key])}")
            for rel in diff[key]:
                print(f"    {rel}")
        lines.append("Бэкап: отсутствуют {missing}, изменены {changed}, лишние {extra}".format(
            **{k: len(v) for k, v in diff.items()}))

    all_errors = scan_errors + hash_errors + backup_errors
    if all_errors:
        print(f"\nНе удалось прочитать файлов: {len(all_errors)}")
        for path, msg in all_errors:
            print(f"  {path}: {msg}")
    lines.append(f"Ошибок чтения: {len(all_errors)}")

    # --- Итоговый отчет ---
    print("\n=== Отчет ===")
    print("\n".join(lines))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"(сохранен в {args.report})")


if __name__ == "__main__":
    main()