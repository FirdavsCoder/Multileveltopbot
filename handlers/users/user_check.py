import asyncpg
from aiogram import types
from loader import dp, db


@dp.my_chat_member_handler()
async def check_user_handler(message: types.ChatMemberUpdated):
    if message.chat.type == 'private':
        status = message.new_chat_member.status
        user_id = message.from_user.id
        if status == 'member':
            await db.update_user_status(status='active', user_id=user_id)
        elif status == 'kicked':
            await db.update_user_status(status='passive', user_id=user_id)
        else:
            await db.update_user_status(status='active', user_id=user_id)
