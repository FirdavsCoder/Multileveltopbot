import logging

from aiogram import types
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from keyboards.default.keyboard import main_menu
from loader import db
from utils.check_channel import check_channel


class UserCheckMiddleware(BaseMiddleware):

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(UserCheckMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        chat_type = message.chat.type
        user_id = message.from_user.id
        if chat_type == types.ChatType.PRIVATE:
            check_user = await db.select_user(user_id=int(user_id))
            if not check_user:
                try:
                    await db.add_user(user_id=int(user_id))
                except Exception as err:
                    print(err)
                    logging.error(err)

                await message.answer(f"👋 <b>Welcome</b> {message.from_user.get_mention(as_html=True)}", reply_markup=main_menu)
                raise CancelHandler()

            if message.text != '/start' and message.text != "/admin":
                check = await db.select_settings()
                if check['value'] == 'True':
                    check = await check_channel(message.from_user.id)
                    if check:
                        await message.delete()
                        text, keyboard = check
                        await message.answer(text=text,
                                             reply_markup=keyboard)
                        raise CancelHandler()
