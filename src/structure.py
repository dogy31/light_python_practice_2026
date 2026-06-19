import os
from datetime import datetime


def collect_structure(root_path, ext_filter=None):
    ext_set = None
    if ext_filter:
        ext_set = {ext.strip().lower() for ext in ext_filter.split(',') if ext.strip()}

    entries = []

    def _recurse(curr_path, rel_dir):
        try:
            names = os.listdir(curr_path)
        except OSError:
            return
        dirs = []
        files = []
        for name in names:
            full = os.path.join(curr_path, name)
            if os.path.isdir(full):
                dirs.append(name)
            else:
                files.append(name)

        for dirname in sorted(dirs):
            entries.append((os.path.join(rel_dir, dirname), "DIR", None, None))
            _recurse(os.path.join(curr_path, dirname), os.path.join(rel_dir, dirname))

        for filename in sorted(files):
            if ext_set is not None:
                ext = os.path.splitext(filename)[1].lstrip('.').lower()
                if ext not in ext_set:
                    continue
            full_path = os.path.join(curr_path, filename)
            try:
                size = os.path.getsize(full_path)
                mtime = os.path.getmtime(full_path)
            except OSError:
                continue
            entries.append((os.path.join(rel_dir, filename), "FILE", size, mtime))

    _recurse(root_path, "")
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
