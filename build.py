# build.py
import PyInstaller.__main__
import os
import subprocess
import sys


def ensure_icon_exists():
    """Проверяет наличие иконки, создаёт если нет"""
    icon_file = 'app_icon.ico'

    if os.path.exists(icon_file):
        return True

    # Запускаем create_icon.py как отдельный скрипт
    result = subprocess.run([sys.executable, "create_icon.py"])
    return result.returncode == 0 and os.path.exists(icon_file)


if __name__ == '__main__':
    icon_exists = ensure_icon_exists()

    args = [
        'app.py',
        '--name=DICOM Converter',
        '--onefile',
        '--windowed',
        '--add-data=templates;templates',
        '--add-data=static;static',
        '--clean'
    ]

    if icon_exists:
        args.insert(3, '--icon=app_icon.ico')
        args.append('--add-data=app_icon.ico:.')

    PyInstaller.__main__.run(args)