import logging

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler

from loader import dp, db
from utils.check_channel import check_channel


@dp.callback_query_handler(lambda call: call.data == "check_channel")
async def check_channel_handler(call: types.CallbackQuery):
    check = await check_channel(call.from_user.id)
    if check:
        await call.answer("☝️Siz hamma kanallarga obuna bo'lmadingiz!", show_alert=True)
        await call.answer()
        raise CancelHandler()
    else:
        await call.message.delete()
        user = await db.select_user(user_id=call.from_user.id)
        try:
            await call.message.edit_text(f"👋 <b>Welcome</b> {call.from_user.get_mention(as_html=True)}")
        except Exception as err:
            logging.error(err)
            await call.message.answer(f"👋 <b>Welcome</b> {call.from_user.get_mention(as_html=True)}")
