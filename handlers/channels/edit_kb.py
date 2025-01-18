from aiogram import types

from loader import dp, db, bot

@dp.channel_post_handler(state=None)
async def channel_post(message: types.Message):
    if message.chat.type == 'channel':
        await message.edit_reply_markup()
    else:
        await message.answer("Bu kanalda post qo'shish mumkin emas!")