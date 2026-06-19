#!/usr/bin/env python3
import os
import sys

from cli import parse_args
from structure import collect_structure, print_structure
from hashing import collect_duplicates, print_duplicates
from compare import compare_folders, print_comparison


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
    entries = collect_structure(root_path, ext_filter=args.filter)
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
        entries_backup = collect_structure(root_backup, ext_filter=args.filter)
        comparison = compare_folders(entries, entries_backup, root_path, root_backup)
        print_comparison(comparison)


if __name__ == "__main__":
    main()
