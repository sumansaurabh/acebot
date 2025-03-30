#!/usr/bin/env python
"""
Скрипт для сборки приложения Interview Corvus для различных операционных систем.
Запуск: poetry run python build.py
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_dirs():
    """Очистить директории сборки."""
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Очищена директория: {dir_name}")


def get_version():
    """Получить версию приложения из модуля."""
    sys.path.append(os.path.abspath("."))
    try:
        from interview_corvus import __version__
        return __version__
    except ImportError:
        print("Не удалось импортировать версию. Используется 'dev'")
        return "dev"


def build_macos():
    """Сборка для macOS."""
    print("\n=== Сборка для macOS ===")
    version = get_version()

    # Создаем временную директорию для приложения
    app_name = "Interview Corvus.app"
    if os.path.exists(f"dist/{app_name}"):
        shutil.rmtree(f"dist/{app_name}")

    # Запускаем PyInstaller
    cmd = [
        "pyinstaller",
        "--clean",
        "--windowed",
        "--name=Interview Corvus",
        "--add-data=resources:resources",
        "--hidden-import=PyQt6.QtSvg",
        "--hidden-import=tiktoken_ext.openai_public",
        "--hidden-import=tiktoken_ext",
        "--hidden-import=keyring.backends.macOS",
        "--osx-bundle-identifier=com.interview.corvus",
        "interview_corvus/main.py"
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.SubprocessError as e:
        print(f"Ошибка при сборке macOS: {e}")
        return

    # Создаем DMG-образ
    print("Создание DMG-образа...")
    dmg_name = f"Interview_Corvus-{version}-macOS.dmg"

    try:
        subprocess.run([
            "hdiutil", "create",
            "-volname", f"Interview Corvus {version}",
            "-srcfolder", f"dist/{app_name}",
            "-ov", "-format", "UDZO",
            f"dist/{dmg_name}"
        ], check=True)
        print(f"macOS сборка завершена: dist/{dmg_name}")
    except subprocess.SubprocessError as e:
        print(f"Ошибка при создании DMG: {e}")
        print(f"Сборка доступна в директории: dist/{app_name}")


def build_windows():
    """Сборка для Windows."""
    print("\n=== Сборка для Windows ===")
    version = get_version()

    # Запускаем PyInstaller с правильным разделителем для Windows
    add_data_param = "resources;resources" if platform.system() == "Windows" else "resources:resources"

    cmd = [
        "pyinstaller",
        "--clean",
        "--windowed",
        "--name=Interview Corvus",
        f"--add-data={add_data_param}",
        "--hidden-import=PyQt6.QtSvg",
        "--hidden-import=tiktoken_ext.openai_public",
        "--hidden-import=tiktoken_ext",
        "--hidden-import=keyring.backends.Windows",
        "interview_corvus/main.py"
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.SubprocessError as e:
        print(f"Ошибка при сборке Windows: {e}")
        return

    # Создаем ZIP-архив
    print("Создание ZIP-архива...")
    output_dir = "dist/Interview Corvus"
    zip_name = f"Interview_Corvus-{version}-Windows.zip"

    try:
        shutil.make_archive(
            base_name=f"dist/{zip_name.replace('.zip', '')}",
            format="zip",
            root_dir="dist",
            base_dir="Interview Corvus"
        )
        print(f"Windows сборка завершена: dist/{zip_name}")
    except Exception as e:
        print(f"Ошибка при создании ZIP-архива: {e}")
        print(f"Сборка доступна в директории: {output_dir}")


def build_linux():
    """Сборка для Linux."""
    print("\n=== Сборка для Linux ===")
    version = get_version()

    # Запускаем PyInstaller
    cmd = [
        "pyinstaller",
        "--clean",
        "--windowed",
        "--name=Interview Corvus",  # Унифицированное имя для всех платформ
        "--add-data=resources:resources",
        "--hidden-import=PyQt6.QtSvg",
        "--hidden-import=tiktoken_ext.openai_public",
        "--hidden-import=tiktoken_ext",
        "--hidden-import=keyring.backends.SecretService",
        "interview_corvus/main.py"
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.SubprocessError as e:
        print(f"Ошибка при сборке Linux: {e}")
        return

    # Создаем TGZ-архив
    print("Создание TGZ-архива...")
    output_dir = "dist/Interview Corvus"
    tgz_name = f"Interview_Corvus-{version}-Linux.tar.gz"

    try:
        subprocess.run([
            "tar", "-czvf",
            f"dist/{tgz_name}",
            "-C", "dist",
            "Interview Corvus"
        ], check=True)
        print(f"Linux сборка завершена: dist/{tgz_name}")
    except subprocess.SubprocessError as e:
        print(f"Ошибка при создании TGZ-архива: {e}")
        print(f"Сборка доступна в директории: {output_dir}")


def check_dependencies():
    """Проверка наличия необходимых зависимостей."""
    missing_deps = []

    # Проверка PyInstaller
    try:
        subprocess.run(["pyinstaller", "--version"],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       check=False)
    except FileNotFoundError:
        missing_deps.append("PyInstaller")

    if missing_deps:
        print("\nВНИМАНИЕ: Отсутствуют следующие зависимости:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("Установите их перед сборкой.")
        return False

    return True


def main():
    """Основная функция."""
    current_os = platform.system()

    print("=== Сборка Interview Corvus ===")
    print(f"Текущая ОС: {current_os}")
    print(f"Версия приложения: {get_version()}")

    # Создаем директорию ресурсов, если её нет
    Path("resources").mkdir(exist_ok=True)

    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)

    # Очищаем предыдущие сборки
    clean_build_dirs()

    # Определяем, какую сборку запускать
    if len(sys.argv) > 1:
        target_os = sys.argv[1].lower()
        if target_os == "macos" or target_os == "darwin":
            build_macos()
        elif target_os == "windows" or target_os == "win":
            build_windows()
        elif target_os == "linux":
            build_linux()
        else:
            print(f"Неизвестная ОС: {target_os}")
            print("Используйте: macos, windows или linux")
    else:
        # Если не указана ОС, собираем для текущей
        if current_os == "Darwin":
            build_macos()
        elif current_os == "Windows":
            build_windows()
        elif current_os == "Linux":
            build_linux()
        else:
            print(
                f"Неподдерживаемая ОС для автоматической сборки: {current_os}")
            print("Пожалуйста, укажите ОС вручную: macos, windows или linux")


if __name__ == "__main__":
    main()