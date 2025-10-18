import asyncio
import sys
import os

# Добавляем корневую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.cli.cli_main import cli_main
from app.cli.bot_main import main as bot_main

async def main():
    """Запускает инициализацию БД, затем бота"""
    print("🚀 Запуск инициализации базы данных...")
    await cli_main()
    print("🎯 Запуск телеграм бота...")
    bot_main()

if __name__ == "__main__":
    asyncio.run(main())