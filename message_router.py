import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем роутер
router = Router()

# URL локального сервера модели
MODEL_SERVER_URL = "http://127.0.0.1:1234/v1/chat/completions"

# Максимальное количество сообщений в контексте
MAX_CONTEXT_MESSAGES = 10

# Флаг для отслеживания первого сообщения от пользователя
user_states = MemoryStorage()

# Создаем объект бота
bot = Bot(token='YOUR_TELEGRAM_BOT_TOKEN_HERE')
dp = Dispatcher(bot, storage=user_states)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляем приветственное сообщение при старте бота"""
    await message.answer("Привет! Я готов помочь. Что тебя интересует?")

@dp.message_handler()
async def handle_message(message: types.Message):
    """Обработчик всех сообщений от пользователя"""
    user_id = message.from_user.id

    # Если пользователь впервые обращается к боту
    if user_id not in user_states:
        user_states[user_id] = {"greeted": True}
        await message.answer("Привет! Что тебя интересует?")
    else:
        try:
            # Добавляем текущее сообщение в контекст
            user_states[user_id]["context"].append(message.text)
            if len(user_states[user_id]["context"]) > MAX_CONTEXT_MESSAGES:
                user_states[user_id]["context"].pop(0)

            # Отправляем запрос к локальной модели
            response = requests.post(
                MODEL_SERVER_URL,
                json={
                    "model": "hermes-3-llama-3.1-8b",
                    "messages": [{"role": "user", "content": message.text}]
                },
                headers={"Content-Type": "application/json"}
            )

            # Проверяем ответ от сервера
            if response.status_code == 200:
                data = response.json()
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Нет ответа")
                await message.answer(reply)
            else:
                await message.answer(f"Ошибка модели: {response.status_code}")
        except Exception as e:
            # Обработка ошибок
            await message.answer(f"Произошла ошибка: {str(e)}")

@dp.message_handler(lambda message: message.text == "Ошибка модели")
async def handle_model_error(message: types.Message):
    """Обработчик сообщений об ошибках модели"""
    await message.answer("Модель временно недоступна. Повторите позже.")

# Запуск polling
if __name__ == "__main__":
    dp.start_polling()