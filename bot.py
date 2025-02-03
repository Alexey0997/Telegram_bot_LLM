import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import message_router

# Загрузка переменных окружения из файла .env
load_dotenv()

async def main():
    # Создаем объект бота
    bot = Bot(
        token=os.getenv("BOT_TOKEN"),  # Токен загружается из файла .env
        default=DefaultBotProperties(parse_mode="HTML")
    )
    
    # Удаляем старые вебхуки и запускаем обработку новых обновлений
    await bot.delete_webhook(drop_pending_updates=True)

    # Создаем диспетчер
    dp = Dispatcher()
    
    # Включаем роутер
    dp.include_router(message_router.router)

    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

