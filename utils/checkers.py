import asyncio
import re
from loader import bot

def validate_telegram_link(link: str) -> dict:
    private_link_regex = r"https://t\.me/c/(\d+)/(\d+)"
    public_link_regex = r"https://t\.me/([\w\d_]+)/(\d+)"
    private_match = re.match(private_link_regex, link)
    if private_match:
        channel_id, message_id = private_match.groups()
        return {
            "channel": f"-100{channel_id}",
            "messageId": int(message_id),
            "message": "SUCCESS"
        }
    public_match = re.match(public_link_regex, link)
    if public_match:
        username, message_id = public_match.groups()
        return {
            "channel": f"{username}",
            "messageId": int(message_id),
            "message": "SUCCESS"
        }

    return {
        "channel": "NONE",
        "messageId": 0,
        "message": "ERROR"
    }


async def check_link_post(chat_id, from_chat_id, message_id):
    try:
        message = await bot.copy_message(chat_id, from_chat_id, message_id)
        await asyncio.sleep(1)
        await bot.delete_message(chat_id, message.message_id)
        return True
    except Exception as e:
        return False