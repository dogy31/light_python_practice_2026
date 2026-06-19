import argparse


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
    parser.add_argument(
        "--filter",
        default=None,
        help="Фильтр по расширениям (comma-separated, без точки), например: 'py,txt'"
    )
    return parser.parse_args()
