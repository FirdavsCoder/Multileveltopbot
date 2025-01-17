import asyncio
import json
import logging
import os
from datetime import datetime
import re
from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InputMediaDocument, InputFile
from aiogram.utils import exceptions

from data.config import ADMINS, MESSAGE_SENDER_COMMAND, DATABASE_INFO
from handlers.admin.key import adminKeyboard
from loader import dp, db, bot
from states.states import AddButtonState, EditButtonState
from utils.checkers import validate_telegram_link, check_link_post


async def bot_checker(bot_token, bot_user) -> dict:
    try:
        new_bot = Bot(token=bot_token)
    except exceptions.ValidationError:
        logging.error("Token validation")
        return dict(status=False, message="<b>Bot tokeni yaroqsiz.</b>")
    try:
        bot_ = await new_bot.get_me()
    except exceptions.Unauthorized:
        logging.error("Telegram unauthorized")
        return dict(status=False, message="<b>Bot tokeni yaroqsiz.</b>")
    if bot_.username.lower() != bot_user.lower():
        logging.error("Invalid username")
        return dict(status=False, message="<b>Bot usernamesi yaroqsiz.</b>")

    return dict(status=True, message="Bot successfully")


@dp.message_handler(Command(commands=['admin', 'panel'], prefixes='./!'), user_id=ADMINS, chat_type='private',
                    state='*')
async def admin_menu_handler(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('ADMIN PANEL', reply_markup=adminKeyboard.menu())


@dp.callback_query_handler(text='panel', user_id=ADMINS, chat_type='private', state='*')
async def stat_handler(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    try:
        await message.message.edit_text('BOSH MENU', reply_markup=adminKeyboard.menu())
    except Exception as e:
        logging.error(e)
        await message.message.delete()
        await message.message.answer('ADMIN PANEL', reply_markup=adminKeyboard.menu())


@dp.callback_query_handler(text='stat', user_id=ADMINS, chat_type='private', state='*')
async def stat_handler(message: types.CallbackQuery, state: FSMContext):
    res = await db.count_all_users()
    all, active, daily, weekly, monthly = (res['all'], res['active'], res['daily_users'],
                                           res['weekly_users'], res['monthly_users'])
    date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    text = f"""<b>🧑🏻‍💻 Botdagi obunachilar: <code>{all}</code> ta


Faol obunachilar: <code>{active}</code> ta
Oxirgi 24 soatda: <code>{daily}</code> ta obunachi qo'shildi
Oxirgi 1 haftada: <code>{weekly}</code> ta obunachi qo'shildi
Oxirgi 1 oyda: <code>{monthly}</code> ta obunachi qo'shildi</b>
"""
    text += f"<b>📅 {date_time}</b>"
    await message.answer()
    await message.message.edit_text(text, reply_markup=adminKeyboard.back_panel())


@dp.callback_query_handler(text='close', user_id=ADMINS, chat_type='private', state='*')
async def channels_settings_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
# Todo: Channels settings
@dp.callback_query_handler(text='channels', user_id=ADMINS, chat_type='private', state='*')
async def channels_settings_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer()
    await call.message.edit_text("KANALLAR SOZLAMALARI", reply_markup=await adminKeyboard.channel_settings())


@dp.callback_query_handler(text='channels_on_off', user_id=ADMINS, chat_type='private', state='*')
async def channels_on_of_handler(call: types.CallbackQuery):
    status = await db.select_settings()
    if status['value'] == 'True':
        text = '❌ Majburiy a\'zolik | O\'chirildi'
        await db.update_settings_status(id=status['id'], value='False')
    else:
        text = '✅ Majburiy a\'zolik | Yoqildi'
        await db.update_settings_status(id=status['id'], value='True')

    await call.answer(text, show_alert=True)
    try:
        await call.message.edit_reply_markup(reply_markup=await adminKeyboard.force_settings())
    except Exception as err:
        logging.error(err)
        await call.message.delete()
        await call.message.answer('KANAL SOZLAMALARI', reply_markup=await adminKeyboard.force_settings())


@dp.callback_query_handler(text='channels_list', user_id=ADMINS, chat_type='private', state='*')
async def channels_list_handler(call: types.CallbackQuery):
    result = await adminKeyboard.channels_list()
    if result:
        await call.message.edit_text("KANALLAR", reply_markup=result)
    else:
        await call.answer("Kanallar mavjud emas!", show_alert=True)


@dp.callback_query_handler(text='bots_list', user_id=ADMINS, chat_type='private', state='*')
async def channels_list_handler(call: types.CallbackQuery):
    result = await adminKeyboard.bots_list()
    if result:
        await call.message.edit_text("Botlar", reply_markup=result)
    else:
        await call.answer("botlar mavjud emas!", show_alert=True)


@dp.callback_query_handler(text='delbot', user_id=ADMINS, chat_type='private', state='*')
async def channels_list_handler(call: types.CallbackQuery):
    result = await adminKeyboard.delete_bots()
    if result:
        await call.message.edit_text("Ochirmoqchi bolgan botingiz ustiga 1marta bosing", reply_markup=result)
    else:
        await call.answer("botlar mavjud emas!", show_alert=True)


@dp.callback_query_handler(lambda c: c.data.startswith('dd_'), user_id=ADMINS, chat_type='private',
                           state='*')
async def delete_channel_handler(call: types.CallbackQuery):
    channel_id = call.data.replace('dd_', '')
    await db.delete_bot(id=int(channel_id))
    await call.message.edit_text("BOT OCHIRILDI!", reply_markup=await adminKeyboard.bots_keyboard())


@dp.callback_query_handler(lambda c: c.data.startswith('channel_'), user_id=ADMINS, chat_type='private', state='*')
async def select_channel_handler(call: types.CallbackQuery):
    await call.answer()
    channel_id = call.data.split('_')[1]
    try:
        channel = await bot.get_chat(channel_id)
        count = await bot.get_chat_member_count(channel_id)
        if count > 1000:
            count = f'{round(count / 1000, 1)}K'
    except Exception as err:
        logging.error(err)
        await call.answer('Kanal topilmadi', show_alert=True)
        return
    text = '<b>'
    text += f'Kanal: {channel.title}\n'
    text += f'Kanal ID: {channel.id}\n'
    text += f'Kanal linki: {channel.invite_link}\n'
    text += f'Kanalga a\'zo: {count}\n'
    text += '</b>'
    await call.message.edit_text(text=text, reply_markup=types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='channels_list')),
                                 disable_web_page_preview=True)


@dp.callback_query_handler(lambda c: c.data == 'delete_channel', user_id=ADMINS, chat_type='private', state='*')
async def delete_channel_handler(call: types.CallbackQuery):
    result = await adminKeyboard.delete_channels()
    if not result:
        await call.answer('Kanallar mavjud emas!', show_alert=True)
        return
    await call.answer()
    await call.message.edit_text('O\'chirish uchun kanalni tanlang', reply_markup=result)


@dp.callback_query_handler(lambda c: c.data.startswith('delete_channel_'), user_id=ADMINS, chat_type='private',
                           state='*')
async def delete_channel_handler(call: types.CallbackQuery):
    channel_id = call.data.replace('delete_channel_', '')
    await db.delete_channel(channel_id=channel_id)
    await call.message.edit_text("KANAL OCHIRILDI!", reply_markup=await adminKeyboard.channel_settings())


class FromChannel(StatesGroup):
    channel_id = State()
    channel_link = State()


@dp.callback_query_handler(text='force_settings', state='*', chat_type='private', user_id=ADMINS)
async def force_settings_handler(call: types.CallbackQuery):
    await call.message.edit_text("<b>Kerakli bo'limni tanlang:</b>", reply_markup=await adminKeyboard.force_settings())


@dp.callback_query_handler(text='bots', state='*', chat_type='private', user_id=ADMINS)
async def bots_handler(call: types.CallbackQuery):
    await call.message.edit_text("<b>Kerakli bo'limni tanlang:</b>", reply_markup=await adminKeyboard.bots_keyboard())


@dp.callback_query_handler(text='bot_add', state='*', chat_type='private', user_id=ADMINS)
async def bot_add_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    bot_ = await bot.get_me()
    await call.message.edit_text(f"<b>1. Birinchi bo‘lib botni({bot_.username}) usernamesini yuboring!</b>",
                                 reply_markup=adminKeyboard.back_panel())
    await state.set_state('FormBot.username')


@dp.message_handler(state='FormBot.username', content_types=['text'], chat_type='private', user_id=ADMINS)
async def bot_user(message: types.Message, state: FSMContext):
    await state.update_data(bot_user=message.text)
    await message.answer("Endi bot tokenini kiriting: ", reply_markup=adminKeyboard.back_panel())
    await state.set_state("FormBot.bot_token")


@dp.message_handler(state='FormBot.bot_token', content_types=['text'], chat_type='private', user_id=ADMINS)
async def bot_user(message: types.Message, state: FSMContext):
    info = await state.get_data()
    result = await bot_checker(bot_token=message.text, bot_user=info['bot_user'])
    if result['status']:
        await state.update_data(bot_token=message.text)
        await message.answer("Endi bot linkini kiriting: ", reply_markup=adminKeyboard.back_panel())
        await state.set_state("FormBot.bot_link")
    else:
        await message.answer("Qandaydir xatolik yuz berdi keyinroq qayta urinb ko'ring!",
                             reply_markup=adminKeyboard.back_panel())
        await state.finish()


@dp.message_handler(state='FormBot.bot_link', content_types=['text'], chat_type='private', user_id=ADMINS)
async def bot_user(message: types.Message, state: FSMContext):
    info = await state.get_data()
    bot_user = info['bot_user']
    bot_token = info['bot_token']
    bot_link = message.text
    result = await db.select_bot(bot_token=str(bot_token))
    if result:
        await message.answer(f'<b>Bot avval qo\'shilgan:</b> @{bot_user}',
                             reply_markup=await adminKeyboard.force_settings())
    else:
        await message.answer(f"<b>@{bot_user} Muvaffaqiyatli qo'shildi ✅</b>",
                             reply_markup=adminKeyboard.back_panel())
        await db.add_bot(bot_token=bot_token, bot_link=bot_link)
    await state.finish()


@dp.callback_query_handler(text='add_channel', user_id=ADMINS, chat_type='private', state='*')
async def add_channel_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    bot_ = await bot.get_me()
    await call.message.edit_text(
        f"<b>1. Birinchi bo‘lib botni(@{bot_.username})"
        f" kanalingizda administrator qiling.\n\n"
        f"2. Administrator qilganingizdan keyn esa kanalingizni"
        f" Public link (@channel)manzilini yoki kanal ID raqamini yuboring (-10012334465)"
        f" yoki kanalingizdan biror bir postni Forward from formatida yuboring</b>",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='channels')))
    await FromChannel.channel_id.set()


@dp.message_handler(user_id=ADMINS, chat_type='private', state=FromChannel.channel_id,
                    content_types=types.ContentType.ANY)
async def channel_id_handler(message: types.Message, state: FSMContext):
    channel_id = None
    channelid = message.text
    if message.forward_from_chat:
        channel_id = str(message.forward_from_chat.id)
    elif channelid.startswith('@'):
        channel_id = str(channelid)
    elif channelid.startswith('-100'):
        channel_id = str(channelid)
    elif channelid.isdigit():
        if not channelid.startswith('-100'):
            channel_id = f'-100{channelid}'
    try:
        channel = await bot.get_chat(channel_id)
        _ = ['creator', 'administrator']
        status = await bot.get_chat_member(channel.id, message.from_user.id)
        if not status.status in _:
            await message.answer(text="Kanal topilmadi",
                                 reply_markup=types.InlineKeyboardMarkup().add(
                                     types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='channels')))
            return
        channel_id = channel.id
        channel_title = channel.title
        channel_link = await channel.export_invite_link()
    except Exception as e:
        logging.error(e)
        await message.answer(text="Kanal topilmadi",
                             reply_markup=types.InlineKeyboardMarkup().add(
                                 types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='channels')))
        return
    result = await db.select_channels(channel_id=str(channel_id))
    if not result:
        await message.answer(text="Yaxshi endi kanal linkni yuboring!")
        await state.update_data(id=channel.id)
        await FromChannel.channel_link.set()
    else:
        await message.answer('<b>Kanal avval qo\'shilgan:</b> <a href="{}">{}</a>'.format(channel_link, channel_title),
                             parse_mode='html', reply_markup=await adminKeyboard.channel_settings())
        await state.finish()


@dp.message_handler(user_id=ADMINS, chat_type='private', state=FromChannel.channel_link)
async def channel_link_handler(message: types.Message, state: FSMContext):
    info = await state.get_data()
    channel_id = info['id']
    try:
        channel = await bot.get_chat(channel_id)
        _ = ['creator', 'administrator']
        status = await bot.get_chat_member(channel.id, message.from_user.id)
        if not status.status in _:
            await message.answer(text="Kanal topilmadi",
                                 reply_markup=types.InlineKeyboardMarkup().add(
                                     types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='channels')))
            return
        channel_id = channel.id
        channel_title = channel.title
        channel_link = await channel.export_invite_link()
    except Exception as e:
        logging.error(e)
        await message.answer(text="Kanal topilmadi",
                             reply_markup=types.InlineKeyboardMarkup().add(
                                 types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='channels')))
        return

    result = await db.add_channel(channel_id=str(channel_id), channel_link=message.text)
    if result:
        await message.answer('<b>Kanal qo\'shildi:</b> <a href="{}">{}</a>'.format(channel_link, channel_title),
                             parse_mode='html', reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='channels')))
        await state.finish()
    else:
        await message.answer(text="Qandaydir xatolik yuz berdi keyinroq qayta urinb ko'ring!",
                             reply_markup=types.InlineKeyboardMarkup().add(
                                 types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='channels')))
        await state.finish()


# Todo: Send message Function
@dp.callback_query_handler(text='location_all', user_id=ADMINS, chat_type='private', state='*')
async def send_users_handler(message: types.CallbackQuery, state: FSMContext):
    nres = await db.select_mailing()
    bot_ = await bot.get_me()
    if nres:
        all_user = await db.count_all_users()
        res = dict(nres)
        user = bot_.username
        id, status, user_id, message_id, reply_markup, mail_type, offset, send, not_send, type, created_at = res.values()
        sends = send + not_send
        if not status:
            tz = False
            status = 'To\'xtatilgan'
        else:
            tz = True
            status = 'Davom etmoqda'
        if type == 'users':
            type = '👤 Userlarga'
        if int(sends) == all_user['active']:
            status = f"<b>📧 Xabar yuborish tugadi</b>"
        date1 = created_at
        date2 = datetime.now()
        interval = date2 - date1
        days = interval.days
        hours, remainder = divmod(interval.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        formattedDuration = [
            f"{days} kun" if days else "",
            f"{hours} soat" if hours else "",
            f"{minutes} daqiqa" if minutes else "",
            f"{remainder} sekund" if remainder else "",
        ]
        duration = ", ".join(filter(None, formattedDuration))
        keyboard = await adminKeyboard.mail_sending(s='s', status=tz)

        text = (f"📨 Xabar yuborish\n\n"
                f"Xabar yuborilmoqda: {type}\n"
                f"✅ Yuborilgan: {send}\n"
                f"❌ Yuborilmagan: {not_send}\n"
                f"👥 Umumiy: {sends}/{all_user['active']}\n"
                f"📊 Status: {status}\n\n"
                f"📅 <b>Habar yuborish uchun sarflangan vaqt:</b> <code>{duration}</code>")
        try:
            await message.message.edit_text(text,
                                            reply_markup=keyboard)
        except Exception as e:
            logging.error(e)
            await message.answer()
        return
    text = ("Foydalanuvchilargaga yuboriladigan xabarni kiriting,"
            " kontent turi ixtiyoriy.\n\n"
            "Foydalanish imkonsiz: location, contact, poll, game, invoice, successful_payment")
    await message.message.edit_text(text,
                                    reply_markup=types.InlineKeyboardMarkup().add(
                                        types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel')))
    await state.set_state('SendFormNoyobKinoBot')


@dp.callback_query_handler(lambda c: c.data.startswith('pause_or_resume|'), user_id=ADMINS, chat_type='private',
                           state='*')
async def location_all_handler(message: types.CallbackQuery, state: FSMContext):
    infolist = message.data.split('|')[1]
    if infolist == 's':
        res = await db.select_mailing()
        if res['status']:
            try:
                os.system("systemctl stop " + MESSAGE_SENDER_COMMAND)
            except Exception as e:
                logging.error(e)
            await db.update_mailing_status(status=False, id=res['id'])
        else:
            try:
                os.system("systemctl restart " + MESSAGE_SENDER_COMMAND)
            except Exception as e:
                logging.error(e)
            await db.update_mailing_status(status=True, id=res['id'])
    nres = await db.select_mailing()
    bot_ = await bot.get_me()
    if nres:
        all_user = await db.count_all_users()
        res = dict(nres)
        user = bot_.username
        id, status, user_id, message_id, reply_markup, mail_type, offset, send, not_send, type, created_at = res.values()
        sends = send + not_send
        if not status:
            tz = False
            status = 'To\'xtatilgan'
        else:
            tz = True
            status = 'Davom etmoqda'
        if type == 'users':
            type = '👤 Userlarga'
        if int(sends) == all_user['active']:
            status = f"<b>📧 Xabar yuborish tugadi</b>"
        date1 = created_at
        date2 = datetime.now()
        interval = date2 - date1
        days = interval.days
        hours, remainder = divmod(interval.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        formattedDuration = [
            f"{days} kun" if days else "",
            f"{hours} soat" if hours else "",
            f"{minutes} daqiqa" if minutes else "",
            f"{remainder} sekund" if remainder else "",
        ]
        duration = ", ".join(filter(None, formattedDuration))
        keyboard = await adminKeyboard.mail_sending(s='s', status=tz)
        text = (f"📨 Xabar yuborish\n\n"
                f"@{user}'da yuborilmoqda: {type}\n"
                f"✅ Yuborilgan: {send}\n"
                f"❌ Yuborilmagan: {not_send}\n"
                f"👥 Umumiy: {sends}/{all_user['active']}\n"
                f"📊 Status: {status}\n\n"
                f"📅 <b>Habar yuborish uchun sarflangan vaqt:</b> <code>{duration}</code>")
        try:
            await message.message.edit_text(text,
                                            reply_markup=keyboard)
        except Exception as e:
            logging.error(e)
            await message.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('delete_mail|'), user_id=ADMINS, chat_type='private',
                           state='*')
async def location_all_handler(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    infolist = message.data.split('|')[1]
    if infolist == 's':
        await db.delete_mailing()
    await message.message.delete()
    await message.message.answer("<b>Xabar yuborish to'xtatildi</b>", reply_markup=adminKeyboard.back_panel())


@dp.message_handler(content_types=['photo', 'voice', 'text', 'sticker', 'animation', 'video', 'video_note', 'audio'],
                    user_id=ADMINS, chat_type='private', state='SendFormNoyobKinoBot')
async def send_users_ads_handler(message: types.Message, state: FSMContext):
    message_id = message.message_id
    reply_markup = ''
    chat_id = message.chat.id
    if message.reply_markup:
        reply_markup = json.dumps(message.reply_markup.as_json(), ensure_ascii=False)

    try:
        os.system("systemctl restart " + MESSAGE_SENDER_COMMAND)
    except Exception as e:
        logging.error(e)
    res = await db.add_new_mailing(user_id=chat_id, message_id=message_id, reply_markup=str(reply_markup),
                                   mail_type='oddiy', type='users')
    if res:

        await message.answer('Xabar yuborish boshlandi')
        await state.finish()
    else:
        await message.answer('Xatolik yuz berdi')
        await state.finish()


@dp.callback_query_handler(state='*', text='ads_bolum', user_id=ADMINS, chat_type='private')
async def ads_bolum_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Kerakli bolimni tanlang:", reply_markup=await adminKeyboard.ads_settings())


@dp.callback_query_handler(state='*', text='add_ads', user_id=ADMINS, chat_type='private')
async def ads_bolum_handler(call: types.CallbackQuery, state: FSMContext):
    res = await db.count_ads()
    if int(res) >= 10:
        await call.answer(
            "Iltmos reklama tugmalarini kamayting eng ko'pi 10tagacha reklama tugmalarini qoshishiz mumkin!",
            show_alert=True)
        return
    await call.message.edit_text("Reklama text kirting!", reply_markup=adminKeyboard.back_panel())
    await state.set_state('ads_add')


@dp.message_handler(content_types=['text'],
                    user_id=ADMINS, chat_type='private', state='ads_add')
async def send_users_ads_handler(message: types.Message, state: FSMContext):
    await db.add_ads(ads_text=message.text)
    await message.answer("Reklama text qoshildi!", reply_markup=adminKeyboard.back_panel())
    await state.finish()


@dp.callback_query_handler(text='delete_ads', state='*', user_id=ADMINS, chat_type='private')
async def delete_ads_handler(call: types.CallbackQuery):
    result = await db.select_all_ads()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    text = "Kerakli reklama ni ochirish uchun tartib raqam boyicha tanlang\n\n"
    for x in result:
        text += f"{x['id']}.{x['ads_text']}\n"
        keyboard.add(types.InlineKeyboardButton(text=x['id'], callback_data=f'pd_{x["id"]}'))
    keyboard.row(types.InlineKeyboardButton(text='⬅️ Ortga', callback_data='panel'))
    await call.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('pd_'), user_id=ADMINS, chat_type='private',
                           state='*')
async def delete_channel_handler(call: types.CallbackQuery):
    channel_id = call.data.replace('pd_', '')
    await db.delete_ads(id=int(channel_id))
    await call.message.edit_text("ADS OCHIRILDI!", reply_markup=await adminKeyboard.ads_settings())


# @dp.callback_query_handler(state='*', text='add_kino', user_id=ADMINS, chat_type='private')
# async def ads_bolum_handler(call: types.CallbackQuery, state: FSMContext):
#     await call.message.edit_text("Kinoni yuboring", reply_markup=adminKeyboard.back_panel())
#     await state.set_state('AddKino.movie')


@dp.message_handler(content_types=types.ContentTypes.VIDEO,
                    user_id=ADMINS, chat_type='private', state='AddKino.movie')
async def send_users_ads_handler(message: types.Message, state: FSMContext):
    file_id = message.video.file_id
    await state.update_data(file_id=file_id)

    await message.answer("Yaxsh endi Kino Nomini yoki tavsifini kiriting:", reply_markup=adminKeyboard.back_panel())
    await state.set_state('AddKino.caption')


@dp.message_handler(content_types=types.ContentTypes.TEXT,
                    user_id=ADMINS, chat_type='private', state='AddKino.caption')
async def send_users_ads_handler(message: types.Message, state: FSMContext):
    await state.update_data(caption=message.text)

    await message.answer("Yaxsh endi Kino kodni yuboring:", reply_markup=adminKeyboard.back_panel())
    await state.set_state('AddKino.code')

@dp.message_handler(content_types=types.ContentTypes.TEXT,
                    user_id=ADMINS, chat_type='private', state='AddKino.code')
async def send_users_ads_handler(message: types.Message, state: FSMContext):
    info = await state.get_data()
    file_id = info['file_id']
    caption = info['caption']
    code = message.text
    if message.text.isdigit():
        result = await db.select_movie(code=int(code))
        if result:
            await message.answer("Kechirasiz avval bu kodda kino joylangan boshqa kod kirting:", reply_markup=adminKeyboard.back_panel())

        else:
            await db.add_movies(code=int(code), caption=caption, file_id=file_id, views=0)
            await message.answer(f"{code} da yangi kino joylandi",
                                 reply_markup=adminKeyboard.back_panel())
            await state.finish()
    else:
        await message.answer("Kino kodi faqat raqam bolish kerak", reply_markup=adminKeyboard.back_panel())

# @dp.callback_query_handler(state='*', text='delete_kino', user_id=ADMINS, chat_type='private')
# async def ads_bolum_handler(call: types.CallbackQuery, state: FSMContext):
#     await call.message.edit_text("Kodni yuboring, ochirilgan kino tiklanmaydi", reply_markup=adminKeyboard.back_panel())
#     await state.set_state('AddKino.moviedelete')

@dp.message_handler(content_types=types.ContentTypes.TEXT,
                    user_id=ADMINS, chat_type='private', state='AddKino.moviedelete')
async def send_users_ads_handler(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.finish()
        await db.delete_movie(code=int(message.text))
        await message.answer("Kino o'chirildi", reply_markup=adminKeyboard.back_panel())
    else:
        await message.answer("Kino kodi faqat raqam bolish kerak", reply_markup=adminKeyboard.back_panel())


@dp.callback_query_handler(state='*', text='buttons_edit', user_id=ADMINS, chat_type='private')
async def buttons_edit_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Kerakli bolimni tanlang:", reply_markup= await adminKeyboard.buttons_edit())


@dp.callback_query_handler(state='*', text='edit_real_exam_questions', user_id=ADMINS, chat_type='private')
async def buttons_edit_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Kerakli bolimni tanlang:", reply_markup=adminKeyboard.edit_real_exam_btn())


@dp.callback_query_handler(state='*', text='edit_general_english_videos', user_id=ADMINS, chat_type='private')
async def buttons_edit_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Kerakli bolimni tanlang:", reply_markup=adminKeyboard.edit_general_english_videos_btn())


@dp.callback_query_handler(text='export_data')
async def export_data(call: types.CallbackQuery, state: FSMContext):
    try:
        # Process start feedback
        await call.answer()
        sended_message = await call.message.edit_text(
            text="❗️ Iltimos, biroz kuting. Jarayon ko'proq vaqt olishi mumkin.")
    except Exception:
        sended_message = None

    try:
        # Define dump file name
        dump_file = f"{DATABASE_INFO['database']}.sql"

        # Use PGPASSWORD environment variable to provide the password
        os.environ['PGPASSWORD'] = DATABASE_INFO['password']

        # Create the command
        command = f"pg_dump -h {DATABASE_INFO['host']} -p 5432 -U {DATABASE_INFO['user']} {DATABASE_INFO['database']} -F c -f {dump_file}"

        # Run the pg_dump command
        result = await asyncio.create_subprocess_shell(command)
        await result.communicate()

        # Clean up environment variable
        os.environ.pop('PGPASSWORD', None)
    except Exception as e:
        print(f"Export error: {e}")
        return

        # Send the backup file
    medias = []
    medias.append(InputMediaDocument(media=InputFile(dump_file)))

    try:
        await call.message.answer_media_group(media=medias)
    except Exception as e:
        print(f"Media sending error: {e}")
        pass

    # Remove the dump file
    try:
        os.remove(dump_file)
    except Exception as e:
        print(f"File removal error: {e}")

    if sended_message:
        try:
            await sended_message.delete()
        except Exception as e:
            print(f"Message deletion error: {e}")


########## BUTTONS HANDLERS
# ADD BUTTON HANDLER
@dp.callback_query_handler(text="add_button")
async def add_button_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await AddButtonState.button_key.set()
    await call.message.answer("Yangi tugma uchun UNIQUE key ni kriting: ", reply_markup=adminKeyboard.back_panel())
    await call.message.delete()



@dp.message_handler(state=AddButtonState.button_key, content_types=types.ContentTypes.TEXT)
async def get_button_key(message: types.Message, state: FSMContext):
    data = await db.select_button(key=message.text)
    if data:
        await message.answer("Bu tugma avval qo'shilgan, boshqa key bilan sinab ko'ring.", reply_markup=adminKeyboard.back_panel())
        await state.finish()
        return
    await state.update_data(button_key=message.text)
    await AddButtonState.next()
    await message.answer("Tugma matnini kiriting: ", reply_markup=adminKeyboard.back_panel())


@dp.message_handler(state=AddButtonState.button_text, content_types=types.ContentTypes.TEXT)
async def get_button_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    button_key = data.get("button_key")
    button_text = message.text
    await db.add_button(key=button_key, text=button_text)
    await message.answer("Tugma qo'shildi", reply_markup=adminKeyboard.menu())
    await state.finish()

# Edit button handler
@dp.callback_query_handler(text_contains="button_edit")
async def edit_button_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await EditButtonState.url.set()
    await state.update_data(button_key=call.data.split(":")[1])
    resources = await db.select_all_resources_by_button_key(call.data.split(":")[1])
    if resources:
        for i in resources:
            data_t = i['url'].split('/')
            del_msg = await bot.copy_message(
                chat_id=call.from_user.id,
                from_chat_id=f"-100{data_t[4]}",
                message_id=data_t[5]
            )
            await bot.send_message(chat_id=call.from_user.id,text=f"O'chiramizmi?", reply_markup=await adminKeyboard.delete_resource_button(i['id']), reply_to_message_id=del_msg.message_id)
    await call.message.answer("Qo'shmoqchi bo'lgan postingizning kanaldagi linkini kiriting: ", reply_markup=adminKeyboard.back_panel())
    await call.message.delete()



@dp.message_handler(state=EditButtonState.url, content_types=types.ContentTypes.TEXT)
async def get_url(message: types.Message, state: FSMContext):
    url = message.text
    checked_link = validate_telegram_link(url)
    if checked_link["message"] == "ERROR":
        await message.answer("Noto'g'ri link kiritildi, iltimos qayta urinib ko'ring")
        return
    check_post = await check_link_post(message.from_user.id, checked_link["channel"], checked_link["messageId"])
    if not check_post:
        await message.answer("Kanaldagi post topilmadi, iltimos qayta urinib ko'ring")
        return
    data = await state.get_data()
    button_key = data.get("button_key")
    await db.add_resource(button_key=button_key, url=url)
    await message.answer("Tugma muvaffaqiyatli o'zgartirildi", reply_markup=await adminKeyboard.buttons_edit())
    await state.finish()

@dp.callback_query_handler(text_contains="delete_resource", state="*")
async def delete_resource_handler(call: types.CallbackQuery):
    res_id = int(call.data.split(":")[1])
    data = await db.select_resource(id=res_id)
    if data:
        await db.delete_resource(id=res_id)
        await call.answer("Resurs o'chirildi", show_alert=True)
        await call.message.delete()
        return
    else:
        await call.answer("Resurs topilmadi", show_alert=True)
        await call.message.delete()
        return
