from aiogram import types

from handlers.admin.key import adminKeyboard
from loader import dp, db, bot

@dp.channel_post_handler(state=None)
async def channel_post(message: types.Message):
    if message.chat.type == 'channel':
        await message.edit_reply_markup(reply_markup=await adminKeyboard.buttons_edit())
    else:
        await message.answer("Bu kanalda post qo'shish mumkin emas!")