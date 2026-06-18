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


def main():
    args = parse_args()
    path = args.path

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


if __name__ == "__main__":
    main()
