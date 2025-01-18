import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import exceptions

from loader import db, bot


class AdminKeyboards():

    def menu(self):
        keyboard = InlineKeyboardMarkup()
        # InlineKeyboardButton(text='⚙️ Reklama bo\'limi', callback_data='ads_bolum')
        keyboard.add(InlineKeyboardButton(text='📊 Statistika', callback_data='stat'),)
        keyboard.row(InlineKeyboardButton(text='⚙️ Majburiy a\'zolik sozlamalari', callback_data='force_settings'))
        keyboard.row(InlineKeyboardButton(text='📝 Xabar yuborish', callback_data='location_all'),
                     InlineKeyboardButton(text='🔘 Buttons', callback_data='buttons_edit'))
        # keyboard.row(InlineKeyboardButton(text='Ma\'lumotlar ombori 📦', callback_data='export_data'))
        keyboard.row(InlineKeyboardButton(text='🔼', callback_data='close'))
        return keyboard

    async def buttons_edit(self, callback_data):
        keyboard = InlineKeyboardMarkup(row_width=2)
        buttons = await db.select_all_buttons()

        year_buttons = []
        skill_buttons = []
        other_buttons = []

        for button in buttons:
            text = button['text']
            if text.isdigit() and len(text) == 4:  # Yil bo'lishi (masalan, 2023)
                year_buttons.append(
                    InlineKeyboardButton(text=text, callback_data=f'{callback_data}:{button["key"]}')
                )
            elif text in ["Listening", "Writing", "Speaking", "Reading"]:  # Maxsus qobiliyat tugmalari
                skill_buttons.append(
                    InlineKeyboardButton(text=text, callback_data=f'{callback_data}:{button["key"]}')
                )
            else:
                other_buttons.append(
                    InlineKeyboardButton(text=text, callback_data=f'{callback_data}:{button["key"]}')
                )

        if year_buttons:
            keyboard.row(*year_buttons)
        if skill_buttons:
            keyboard.row(*skill_buttons)
        for i in range(0, len(other_buttons), 2):
            keyboard.row(*other_buttons[i:i + 2])

        if callback_data == 'button_edit':
            keyboard.row(InlineKeyboardButton(text="➕ Tugma qo'shish", callback_data="add_button"))
            keyboard.row(InlineKeyboardButton(text='🔙 Orqaga', callback_data='panel'))

        return keyboard


    async def delete_resource_button(self, resource_id):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='❌ O\'chirish', callback_data=f'delete_resource:{resource_id}'))
        return keyboard


    def back_panel(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))
        return keyboard

    def edit_real_exam_btn(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton("2023", callback_data="button_edit|2023"),
                    InlineKeyboardButton("2024", callback_data="button_edit|2024"),
                    InlineKeyboardButton("2025", callback_data="button_edit|2025"),
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data="buttons_edit"),
                ]
            ]
        )
        return keyboard

    def edit_general_english_videos_btn(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton("Writing",callback_data="button_edit|writing"),
                    InlineKeyboardButton("Speaking", callback_data="button_edit|speaking"),
                ],
                [
                    InlineKeyboardButton("Listening", callback_data="button_edit|listening"),
                    InlineKeyboardButton("Reading", callback_data="button_edit|reading"),
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data="buttons_edit"),
                ]
            ]
        )
        return keyboard

    async def force_settings(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text='📢 Kanallar', callback_data='channels'))
        status = await db.select_settings()
        if status['value'] == 'True':
            text = '✅ Majburiy a\'zolik | Yoqilgan'
        else:
            text = '❌ Majburiy a\'zolik | O\'chirilgan'
        keyboard.row(InlineKeyboardButton(text=text, callback_data='channels_on_off'))
        keyboard.row(InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))

        return keyboard

    async def channel_settings(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='📢 Kanallar', callback_data='channels_list'))
        keyboard.row(InlineKeyboardButton(text='➕ Kanal qo\'shish', callback_data='add_channel'),
                     InlineKeyboardButton(text='➖ Kanal o\'chirish', callback_data='delete_channel'))
        keyboard.row(InlineKeyboardButton(text='⬅️ Ortga', callback_data='force_settings'))

        return keyboard

    async def ads_settings(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='➕ ADS qo\'shish', callback_data='add_ads'),
                     InlineKeyboardButton(text='➖ ADS o\'chirish', callback_data='delete_ads'))
        keyboard.row(InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))

        return keyboard

    async def bots_keyboard(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='📢 Botlar', callback_data='bots_list'))
        keyboard.row(InlineKeyboardButton(text='➕ Bot qo\'shish', callback_data='bot_add'),
                     InlineKeyboardButton(text='➖ Bot o\'chirish', callback_data='delbot'))
        keyboard.row(InlineKeyboardButton(text='🔙 Orqaga', callback_data='force_settings'))
        return keyboard

    async def channels_list(self):
        keyboard = InlineKeyboardMarkup()
        result = await db.select_all_channels()
        if result:
            for channel in result:
                try:
                    channel = await bot.get_chat(channel['channel_id'])
                    count = (await bot.get_chat_member_count(channel.id))
                    if count > 1000:
                        count = f'{round(count / 1000, 1)}K'
                except Exception as e:
                    logging.error(e)
                    continue
                keyboard.row(
                    InlineKeyboardButton(text=f'{channel.title} [{count}]', callback_data=f'channel_{channel.id}'))
            keyboard.row(InlineKeyboardButton(text='⬅️ Ortga', callback_data='channels'))

            return keyboard
        else:
            return False

    async def bots_list(self):
        try:
            keyboard = InlineKeyboardMarkup(row_width=1)
            result = await db.select_all_bots()
            if result:
                for x in result:
                    try:
                        bot = Bot(token=x['bot_token'])
                        title = await bot.get_me()
                    except exceptions.ValidationError:
                        logging.error("Token validation")
                        continue
                    except exceptions.Unauthorized:
                        logging.error("Telegram unauthorized")
                        continue
                    keyboard.add(InlineKeyboardButton(text=f"{title.full_name}", url=f"{x['bot_link']}"))

                keyboard.row(InlineKeyboardButton(text='⬅️ Ortga', callback_data='bots'))

                return keyboard
            else:
                return False
        except:
            return False

    async def delete_channels(self):
        keyboard = InlineKeyboardMarkup()
        result = await db.select_all_channels()
        if result:
            for channel in result:
                try:
                    channel = await bot.get_chat(channel['channel_id'])
                    count = (await bot.get_chat_member_count(channel.id))
                    if count > 1000:
                        count = f'{round(count / 1000, 1)}K'
                except Exception as e:
                    logging.error(e)
                    continue
                keyboard.row(
                    InlineKeyboardButton(text=f'{channel.title} [{count}]',
                                         callback_data=f'delete_channel_{channel.id}'))
            keyboard.row(InlineKeyboardButton(text='⬅️ Ortga', callback_data='channels'))

            return keyboard
        else:
            return False

    async def delete_bots(self):
        try:
            keyboard = InlineKeyboardMarkup(row_width=1)
            result = await db.select_all_bots()
            if result:
                for x in result:
                    try:
                        bot = Bot(token=x['bot_token'])
                        title = await bot.get_me()
                    except exceptions.ValidationError:
                        logging.error("Token validation")
                        continue
                    except exceptions.Unauthorized:
                        logging.error("Telegram unauthorized")
                        continue
                    keyboard.add(InlineKeyboardButton(text=f"{title.full_name}", callback_data=f'dd_{x["id"]}'))

                keyboard.row(InlineKeyboardButton(text='⬅️ Ortga', callback_data='bots'))

                return keyboard
            else:
                return False
        except:
            return False
    async def mail_sending(self, s: str, status=None):
        keyboard = InlineKeyboardMarkup(row_width=1)
        if status:
            pause_or_resume = "To'xtatish ⏸"
        else:
            pause_or_resume = 'Davom etish ▶️'

        if status != None:
            keyboard.add(InlineKeyboardButton(text=pause_or_resume, callback_data=f'pause_or_resume|{s}'))
        keyboard.add(InlineKeyboardButton(text="🔄 Yangilash", callback_data=f'location_all'))
        keyboard.add(InlineKeyboardButton(text="🗑 O'chirish", callback_data=f'delete_mail|{s}'))
        keyboard.add(InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))

        return keyboard


adminKeyboard = AdminKeyboards()
