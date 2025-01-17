import asyncpg
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.default.keyboard import main_menu, real_exam_btn, full_multilevel_btn
from loader import dp, db, bot
from data.config import ADMINS


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(f"👋 <b>Welcome</b> {message.from_user.get_mention(as_html=True)}!", reply_markup=main_menu)


@dp.message_handler(text="🔙 Orqaga")
async def back(message: types.Message):
    await message.answer("Main menu", reply_markup=main_menu)

@dp.message_handler(state="*")
async def bot_echo(message: types.Message, state: FSMContext):
    await state.finish()
    data = await db.select_button(text=message.text)
    if data:
        data_res = await db.get_all_resources_by_button_key(button_key=data[0]['key'])
        if data_res:
            for i in data_res:
                data_t = i['url'].split('/')
                await bot.copy_message(
                    chat_id=message.from_user.id,
                    from_chat_id=f"-100{data_t[4]}",
                    message_id=data_t[5]
                )
        else: await message.answer("No data found for this button")
        if message.text == "📑 Real Exam Questions":
            await message.answer("Choose the option you want to see:", reply_markup=real_exam_btn)
        elif message.text == "📚 Full Multi-Level Lessons":
            await message.answer("Choose the option you want to see:", reply_markup=full_multilevel_btn)
    else:
        await message.answer("Choose: ", reply_markup=main_menu)