import os
from datetime import datetime


def collect_structure(root_path, ext_filter=None):
    """Собрать структуру. Если ext_filter указан как строка 'py,txt',
    то включать только файлы с этими расширениями (без точки).
    """
    ext_set = None
    if ext_filter:
        ext_set = {ext.strip().lower() for ext in ext_filter.split(',') if ext.strip()}

    entries = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        rel_dir = os.path.relpath(dirpath, root_path)
        if rel_dir == ".":
            rel_dir = ""
        for dirname in sorted(dirnames):
            entries.append((os.path.join(rel_dir, dirname), "DIR", None, None))
        for filename in sorted(filenames):
            # apply extension filter if provided
            if ext_set is not None:
                ext = os.path.splitext(filename)[1].lstrip('.').lower()
                if ext not in ext_set:
                    continue
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
