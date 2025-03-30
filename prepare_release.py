#!/usr/bin/env python
"""
Скрипт для подготовки релиза Interview Corvus.
Собирает все необходимые файлы для релиза на GitHub.
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_version():
    """Получить версию приложения."""
    sys.path.append(os.path.abspath("."))
    from interview_corvus import __version__
    return __version__


def create_release_dir():
    """Создать директорию для релиза."""
    version = get_version()
    release_dir = Path(f"release/interview-corvus-{version}")
    release_dir.mkdir(parents=True, exist_ok=True)
    return release_dir


def copy_release_files(release_dir):
    """Копировать файлы релиза."""
    # Копируем все файлы из dist
    dist_dir = Path("dist")
    if not dist_dir.exists() or not any(dist_dir.iterdir()):
        print("ОШИБКА: Директория dist пуста или не существует.")
        print("Сначала выполните сборку приложения с помощью build.py")
        sys.exit(1)

    # Копируем все файлы релиза
    for file_path in dist_dir.glob("Interview_Corvus-*"):
        if file_path.is_file():
            print(f"Копирование {file_path} -> {release_dir / file_path.name}")
            shutil.copy2(file_path, release_dir / file_path.name)

    # Копируем README и другие важные файлы
    for file_name in ["README.md", "LICENSE"]:
        if Path(file_name).exists():
            shutil.copy2(file_name, release_dir / file_name)


def create_checksums(release_dir):
    """Создать файлы с контрольными суммами."""
    print("Создание контрольных сумм...")

    with open(release_dir / "checksums.txt", "w") as f:
        f.write(f"# Interview Corvus {get_version()} checksums\n")
        f.write(
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for file_path in release_dir.glob("Interview_Corvus-*"):
            if file_path.is_file():
                # MD5
                md5 = subprocess.check_output(
                    ["md5sum" if sys.platform != "darwin" else "md5",
                     str(file_path)],
                    text=True
                ).split()[0]

                # SHA256
                sha256 = subprocess.check_output(
                    ["sha256sum" if sys.platform != "darwin" else "shasum",
                     "-a", "256", str(file_path)],
                    text=True
                ).split()[0]

                f.write(f"{file_path.name}:\n")
                f.write(f"  MD5: {md5}\n")
                f.write(f"  SHA256: {sha256}\n\n")


def create_release_notes(release_dir):
    """Создать файл с заметками о релизе."""
    version = get_version()

    with open(release_dir / "RELEASE_NOTES.md", "w") as f:
        f.write(f"# Interview Corvus {version} Release Notes\n\n")
        f.write(f"Release Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")

        f.write("## Что нового\n\n")
        f.write("- Первый публичный релиз\n")
        f.write("- Поддержка Windows, macOS и Linux\n\n")

        f.write("## Системные требования\n\n")
        f.write("### Windows\n")
        f.write("- Windows 10 или более новая версия\n")
        f.write("- 4 ГБ ОЗУ (рекомендуется 8 ГБ)\n")
        f.write("- 500 МБ свободного места на диске\n\n")

        f.write("### macOS\n")
        f.write("- macOS Catalina (10.15) или более новая версия\n")
        f.write("- 4 ГБ ОЗУ (рекомендуется 8 ГБ)\n")
        f.write("- 500 МБ свободного места на диске\n\n")

        f.write("### Linux\n")
        f.write(
            "- Современный дистрибутив Linux (Ubuntu 20.04+, Fedora 34+, и т.д.)\n")
        f.write("- 4 ГБ ОЗУ (рекомендуется 8 ГБ)\n")
        f.write("- 500 МБ свободного места на диске\n")
        f.write("- X11 или Wayland с Qt поддержкой\n\n")

        f.write("## Установка\n\n")
        f.write("### Windows\n")
        f.write("1. Распакуйте ZIP-архив\n")
        f.write("2. Запустите `Interview Corvus.exe`\n\n")

        f.write("### macOS\n")
        f.write("1. Смонтируйте DMG-образ\n")
        f.write("2. Перетащите `Interview Corvus.app` в папку Applications\n")
        f.write(
            "3. При первом запуске: Ctrl+клик по приложению, выберите 'Открыть'\n\n")

        f.write("### Linux\n")
        f.write(
            "1. Распакуйте архив: `tar -xzf Interview_Corvus-*-Linux.tar.gz`\n")
        f.write("2. Запустите: `./interview-corvus/interview-corvus`\n\n")

        f.write("## Известные проблемы\n\n")
        f.write("- Для корректной работы требуется API ключ OpenAI\n")


def create_github_release_template(release_dir):
    """Создать шаблон для релиза на GitHub."""
    version = get_version()

    with open(release_dir / "GITHUB_RELEASE_TEMPLATE.md", "w") as f:
        f.write(f"# Interview Corvus {version}\n\n")
        f.write(
            "Interview Corvus - невидимый помощник с искусственным интеллектом для технических собеседований.\n\n")

        f.write("## Загрузки\n\n")
        f.write("- [Windows (.zip)](link-to-windows-zip)\n")
        f.write("- [macOS (.dmg)](link-to-macos-dmg)\n")
        f.write("- [Linux (.tar.gz)](link-to-linux-tar-gz)\n\n")

        f.write(
            "SHA-256 контрольные суммы доступны в файле `checksums.txt`\n\n")

        f.write("## Что нового\n\n")
        f.write("- Первый публичный релиз\n")
        f.write("- Поддержка Windows, macOS и Linux\n\n")

        f.write("## Системные требования\n\n")
        f.write(
            "- Windows 10+, macOS 10.15+, или современный Linux дистрибутив\n")
        f.write("- 4 ГБ ОЗУ (рекомендуется 8 ГБ)\n")
        f.write("- 500 МБ свободного места на диске\n\n")

        f.write(
            "Подробную информацию смотрите в [RELEASE_NOTES.md](link-to-release-notes)\n")


def main():
    """Основная функция."""
    print(f"=== Подготовка релиза Interview Corvus {get_version()} ===")

    # Создаем директорию для релиза
    release_dir = create_release_dir()
    print(f"Создана директория релиза: {release_dir}")

    # Копируем файлы релиза
    copy_release_files(release_dir)

    # Создаем контрольные суммы
    create_checksums(release_dir)

    # Создаем заметки о релизе
    create_release_notes(release_dir)

    # Создаем шаблон для GitHub релиза
    create_github_release_template(release_dir)

    print(f"\nПодготовка релиза завершена. Файлы находятся в {release_dir}")


if __name__ == "__main__":
    main()