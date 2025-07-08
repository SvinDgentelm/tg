from aiogram import Router, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message
from aiogram import types
from create_bot import database
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
from create_bot import database,scheduler,bot,panel



main_menu_router = Router()

#main_menu---------------------------------------

@main_menu_router.callback_query(F.data == 'main_menu')
async def main_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()

    user = database.get_user(callback.from_user.id)
    slot = database.get_slot(user[2])

    text = '''
✔️ Наш VPN один из самых быстрых и безопасных!
✔️ Используется VPN протокол, который устойчив к любым блокировкам!
✔️ Поддерживается бесперебойная работа и высокая скорость соединения!

💰 Тарифы для 3 устройств:
└ 200 рублей на 1 мес
└ 500 рублей на 3 мес
└ 900 рублей на 6 мес

    '''


    if slot != None:
        builder.row(types.InlineKeyboardButton(
            text='Моя подписка 🥸',
            callback_data='user_slot_info'
        ))
        text += '\n👉 Для подключения VPN, нажми на кнопку "Моя подписка 🥸" и следуй инструкциям.'
    else:
        builder.row(types.InlineKeyboardButton(
            text='Подключить VPN 💎',
            callback_data='shop_plan'
        ))
        text += '\n👉 Для получения доступа к VPN, нажми на кнопку "Подключить VPN 💎" выбери тариф и следуй инструкциям.'
    
    builder.row(types.InlineKeyboardButton(
        text='Баланс 💰',
        callback_data='balance'
    ))

    builder.row(types.InlineKeyboardButton(
        text='Поделиться 🎖',
        callback_data='referral_program'
    ))


    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback.answer()

@main_menu_router.message(CommandStart())
@main_menu_router.message(Command('main_menu'))
async def main_menu(message: Message, command: CommandObject):
    builder = InlineKeyboardBuilder()
    
    if command.command == 'start':
        if command.args:
            
            user_id = message.from_user.id
            user = database.get_user(user_id=user_id)
            ref_link = command.args

            if not user[6]:

                OK = InlineKeyboardBuilder()
                OK.row(types.InlineKeyboardButton(text='OK', callback_data='del_message'))

                database.add_ref_link(user_id=user_id, ref_link=ref_link)
                await bot.send_message(chat_id=user_id, text='<b>Реферальная ссылка активна!</b>\n\nПополните баланс чтобы получить награду',
                                        reply_markup=OK.as_markup())

    user = database.get_user(message.from_user.id)
    slot = database.get_slot(user[2])

    text = '''
✔️ Наш VPN один из самых быстрых и безопасных!
✔️ Используется VPN протокол, который устойчив к любым блокировкам!
✔️ Поддерживается бесперебойная работа и высокая скорость соединения!

💰 Тарифы для 3 устройств:
└ 200 рублей на 1 мес
└ 500 рублей на 3 мес
└ 900 рублей на 6 мес

    '''


    if slot != None:
        builder.row(types.InlineKeyboardButton(
            text='Моя подписка 🥸',
            callback_data='user_slot_info'
        ))
        text += '\n👉 Для подключения VPN, нажми на кнопку "Моя подписка 🥸" и следуй инструкциям.'
    else:
        builder.row(types.InlineKeyboardButton(
            text='Подключить VPN 💎',
            callback_data='shop_plan'
        ))
        text += '\n👉 Для получения доступа к VPN, нажми на кнопку "Подключить VPN 💎" выбери тариф и следуй инструкциям.'
    
    builder.row(types.InlineKeyboardButton(
        text='Баланс 💰',
        callback_data='balance'
    ))

    builder.row(types.InlineKeyboardButton(
        text='Поделиться 🎖',
        callback_data='referral_program'
    ))

    await message.answer(text=text, reply_markup=builder.as_markup())

#main_menu---------------------------------------

@main_menu_router.callback_query(F.data=='del_message')
async def del_message(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()