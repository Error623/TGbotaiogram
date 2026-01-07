import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import BaseMiddleware
from aiogram.types import Message
from dotenv import load_dotenv
from keyboards import main_menu, yes_no 
from states import Funnel, Survey
from db import create_tables, add_lead, get_leads_for_reminder, mark_reminder_sent

# ---------- LOGGING ----------
class LogingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            logger.info(
                f"MIDDLEWARE | user_id={event.from_user.id} | text={event.text}"
            )
        return await handler(event, data)

logger = logging.getLogger(__name__)

# ---------- ENV ----------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ---------- BOT ----------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ---------- HANDLERS ----------
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    logger.info(f"START | user_id={message.from_user.id}")
    await message.answer("Привет! Как вас зовут?", reply_markup=main_menu())
    await state.set_state(Survey.name)

@dp.message(Survey.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите телефон:")
    await state.set_state(Survey.phone)

@dp.message(Survey.phone)
async def get_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()

    add_lead (
        tg_id=message.from_user.id,
        name=data['name'],
        phone=message.text
    )

    text = (
        "🔥 Новая заявка\n\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {message.text}\n"
        f"Telegram: @{message.from_user.username or '-'}"
    )

    await bot.send_message(ADMIN_ID, text)
    await message.answer("Спасибо! Заявка отправлена ✅")
    await state.clear()

@dp.callback_query(lambda c: c.data == "form") 
async def form_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Готовы начать?",
        reply_markup=yes_no()
    )
    await state.set_state(Funnel.waiting_decision) 
    await callback.answer()


@dp.callback_query(Funnel.waiting_decision, lambda c: c.data == "yes")  
async def yes(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ваше имя")
    await state.set_state(Funnel.waiting_name)
    await callback.answer()

@dp.callback_query(Funnel.waiting_decision, lambda c: c.data == "no") 
async def no(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Хорошо, обращайтесь позже!")
    await state.clear()
    await callback.answer()


@dp.message(Funnel.waiting_name)
async def get_name_funnel(message: types.Message, state: FSMContext): 
    await state.update_data(name=message.text)
    await message.answer("Хорошо, мы с вами свяжемся!")
    await state.clear()



@dp.message()
async def all_messages(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    logger.info(
        f"MESSAGE | user_id={message.from_user.id} | "
        f"state={current_state} | text={message.text}"
    )


async def reminder_worker(bot: Bot,):
    while True:
        leads = get_leads_for_reminder()

        for lead_id, tg_id in leads:
            try:
                await bot.send_message(
                    tg_id, 
                    "Напоминание о вашей заявке. Если актуально - напишите нам"
                )
                mark_reminder_sent(lead_id)
            except:
                pass

            await asyncio.sleep(60 * 60)

# ---------- MAIN ----------

async def main():
    logger.info("Бот запущен")
    create_tables()
    asyncio.create_task(reminder_worker(bot))
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    asyncio.run(main())
