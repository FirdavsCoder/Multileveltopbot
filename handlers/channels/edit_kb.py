from aiogram import types

from handlers.admin.key import adminKeyboard
from loader import dp, db, bot

@dp.channel_post_handler(state=None)
async def channel_post(message: types.Message):
    if message.chat.type == 'channel':
        await message.edit_reply_markup(reply_markup=await adminKeyboard.buttons_edit('add_from_channel'))
    else:
        await message.answer("Bu kanalda post qo'shish mumkin emas!")

@dp.callback_query_handler(text_contains='add_from_channel')
async def add_from_channel(call: types.CallbackQuery):
    button_key = call.data.split(':')[1]
    channel_id = call.message.chat.id
    post_id = call.message.message_id
    link = f"https://t.me/{channel_id}/{post_id}"
    await db.add_resource(button_key=button_key, url=link)
    await bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=None
    )
    await call.answer("Post muvaffaqiyatli qo'shildi!")