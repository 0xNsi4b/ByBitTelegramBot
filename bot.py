import asyncio
import logging
import subprocess
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import config
import pandas as pd


admin = int(config.info.admin.get_secret_value())
dp = Dispatcher()
bot = Bot(token=config.info.telegram_bot_api.get_secret_value())
logging.basicConfig(level=logging.INFO)


process = None


@dp.message(Command('start'))
async def work(message: Message):
    if message.from_user.id == admin:
        await message.answer('/start_bot - Запускает бота на неработающие пары \n'
                             '/stop_bot - Выключает пару и удаляет ее \n'
                             '/show_settings - Показывает установленные настройки \n')
    else:
        await message.answer('Вы не являетесь администратором.')


@dp.message(Command('start_bot'))
async def start_futures_bot(message: Message):
    if message.from_user.id == admin:
        global process
        if process is None:
            command = [
                'python',
                'models.py',
            ]
            process = subprocess.Popen(command)
            await message.answer('Запустил бота')
        else:
            await message.answer('Бот уже запущен')
    else:
        await message.answer('Вы не являетесь администратором.')


@dp.message(Command('stop_bot'))
async def stop(message: Message):
    if message.from_user.id == admin:
        global process
        if process is not None:
            process.terminate()
            process = None
            await message.answer('Выключил бота')
        else:
            await message.answer('Бот уже выключен')
    else:
        await message.answer('Вы не являетесь администратором.')


@dp.message()
async def stop(message: Message):
    if message.from_user.id == admin:
        if 'leverage' in message.text.lower():
            leverage = message.text.split()[1]
            df = pd.read_csv('settings.csv')
            df['leverage'][0] = int(leverage)
            df.to_csv('settings.csv', index=False)
            await message.reply(f'Вы имзменили leverage на {leverage}')

        if 'stop' in message.text.lower():
            stop_lose = message.text.split()[1]
            df = pd.read_csv('settings.csv')
            df['stop'][0] = float(stop_lose)
            df.to_csv('settings.csv', index=False)
            await message.reply(f'Вы имзменили stop на {stop_lose}')

        if 'profit' in message.text.lower():
            profit = message.text.split()[1]
            df = pd.read_csv('settings.csv')
            df['profit'][0] = float(profit)
            df.to_csv('settings.csv', index=False)
            await message.reply(f'Вы имзменили profit на {profit}')

    else:
        await message.answer('Вы не являетесь администратором.')


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
