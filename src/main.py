#!/usr/bin/env python3
import argparse
import hashlib
import os
import sys
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description="Утилита сканирует папку и показывает структуру проекта."
    )
    parser.add_argument("path", help="Путь к папке для сканирования")
    parser.add_argument(
        "--backup",
        default=None,
        help="Путь к резервной копии для сравнения"
    )
    return parser.parse_args()


def collect_structure(root_path):
    entries = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        rel_dir = os.path.relpath(dirpath, root_path)
        if rel_dir == ".":
            rel_dir = ""
        for dirname in sorted(dirnames):
            entries.append((os.path.join(rel_dir, dirname), "DIR", None, None))
        for filename in sorted(filenames):
            full_path = os.path.join(dirpath, filename)
            size = os.path.getsize(full_path)
            mtime = os.path.getmtime(full_path)
            entries.append((os.path.join(rel_dir, filename), "FILE", size, mtime))
    return entries


def format_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def print_structure(root_path, entries):
    print(f"Сканируемая папка: {root_path}")
    print("Структура проекта:")
    if not entries:
        print("  (папка пуста)")
        return
    for rel_path, entry_type, size, mtime in entries:
        if not rel_path:
            continue
        if entry_type == "FILE":
            date_str = format_datetime(mtime)
            print(f"  [{entry_type}] {rel_path} | {size} байт | {date_str}")
        else:
            print(f"  [{entry_type}] {rel_path}")


def compute_hash(path):
    hasher = hashlib.sha256()
    with open(path, "rb") as file:
        while True:
            chunk = file.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def collect_duplicates(root_path, entries):
    duplicates = {}
    for rel_path, entry_type, size, mtime in entries:
        if entry_type != "FILE":
            continue
        full_path = os.path.join(root_path, rel_path)
        file_hash = compute_hash(full_path)
        duplicates.setdefault(file_hash, []).append(rel_path)
    return duplicates


def print_duplicates(duplicates):
    print("\nГруппы дубликатов:")
    found = False
    for file_hash, paths in duplicates.items():
        if len(paths) < 2:
            continue
        found = True
        print(f"  Хеш {file_hash}:")
        for path in paths:
            print(f"    - {path}")
    if not found:
        print("  Дубликаты не найдены.")


def compare_folders(entries_src, entries_backup, root_src, root_backup):
    src_files = {rel_path: (size, mtime) for rel_path, entry_type, size, mtime in entries_src if entry_type == "FILE"}
    backup_files = {rel_path: (size, mtime) for rel_path, entry_type, size, mtime in entries_backup if entry_type == "FILE"}

    missing = set(src_files.keys()) - set(backup_files.keys())
    extra = set(backup_files.keys()) - set(src_files.keys())
    changed = []

    for path in src_files.keys() & backup_files.keys():
        if src_files[path] != backup_files[path]:
            changed.append(path)

    return {"missing": missing, "extra": extra, "changed": changed}


def print_comparison(comparison):
    print("\nСравнение с резервной копией:")
    missing = comparison["missing"]
    extra = comparison["extra"]
    changed = comparison["changed"]

    if missing:
        print("  Отсутствуют в бэкапе:")
        for path in sorted(missing):
            print(f"    - {path}")
    if extra:
        print("  Лишние в бэкапе:")
        for path in sorted(extra):
            print(f"    - {path}")
    if changed:
        print("  Изменены:")
        for path in sorted(changed):
            print(f"    - {path}")
    if not missing and not extra and not changed:
        print("  Папки идентичны.")


def main():
    args = parse_args()
    path = args.path
    backup_path = args.backup

    if not os.path.exists(path):
        print(f"Ошибка: путь не найден: {path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(path):
        print(f"Ошибка: указанный путь не папка: {path}", file=sys.stderr)
        sys.exit(1)

    root_path = os.path.abspath(path)
    entries = collect_structure(root_path)
    print_structure(root_path, entries)
    duplicates = collect_duplicates(root_path, entries)
    print_duplicates(duplicates)

    if backup_path:
        if not os.path.exists(backup_path):
            print(f"Ошибка: путь к бэкапу не найден: {backup_path}", file=sys.stderr)
            sys.exit(1)
        if not os.path.isdir(backup_path):
            print(f"Ошибка: путь к бэкапу не папка: {backup_path}", file=sys.stderr)
            sys.exit(1)
        root_backup = os.path.abspath(backup_path)
        entries_backup = collect_structure(root_backup)
        comparison = compare_folders(entries, entries_backup, root_path, root_backup)
        print_comparison(comparison)


if __name__ == "__main__":
    main()
