from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import types
from create_bot import database, panel
from aiogram.utils.keyboard import InlineKeyboardBuilder


con_sub_router = Router()

#connect_sub----------------------------------

@con_sub_router.callback_query(F.data == 'set_slot')
async def copy_key(callback: CallbackQuery):

    user_id = callback.from_user.id
    slot = database.get_slot(user_id=user_id)
    
    builder= InlineKeyboardBuilder()
    
    builder.add(types.InlineKeyboardButton(text='IOS 🍏', callback_data='connect_ios'))
    builder.add(types.InlineKeyboardButton(text='Android 🤖', callback_data='connect_android'))

    builder.row(types.InlineKeyboardButton(text='Windows 🖥', callback_data='connect_windows'))
    builder.add(types.InlineKeyboardButton(text='MacOs 💻', callback_data='connect_macos'))


    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='user_slot_info'
    ))
    
    text='<b>Подключить VPN очень просто!</b>\n\nВыберите вашу платформу для подключения'


    
    if slot[1] == callback.from_user.id:

        await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
        await callback.answer()

    else:
        await callback.message.edit_text('Произошла ошибка, вернитесь на главную', reply_markup=builder.as_markup())
        await callback.answer()



@con_sub_router.callback_query(F.data == 'connect_ios')
async def connect_ios(callback: CallbackQuery):

    builder = InlineKeyboardBuilder()

    link = panel.link(callback.from_user.id)

    text=f'1️⃣ Установите любое приложение по кнопкам ниже (или используйте любой другой Xray клиент)\n\n2️⃣ Скопируйте ключ подключения ниже в сообщении\n\n3️⃣ В приложении нажмите на *"+"* и выберите *"вставить"* или *"Добавить из буфера"*'
    text += f'\n\n4️⃣*VPN Настроен и к готов работе* \n\n*КЛЮЧ ПОДКЛЮЧЕНИЯ:* \n\n`{link}`'

    builder.row(types.InlineKeyboardButton(text='Установить Streisand ♥️', url='https://apps.apple.com/us/app/streisand/id6450534064'))
    builder.row(types.InlineKeyboardButton(text='Установить v2RayTun ♠️', url='https://apps.apple.com/ru/app/v2raytun/id6476628951'))
    builder.row(types.InlineKeyboardButton(text='Установить V2Box ♦️', url='https://apps.apple.com/ru/app/v2box-v2ray-client/id6446814690'))

    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='set_slot'
    ))

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode='Markdown')
    await callback.answer()


@con_sub_router.callback_query(F.data == 'connect_windows')
async def connect_ios(callback: CallbackQuery):

    builder = InlineKeyboardBuilder()

    link = panel.link(callback.from_user.id)

    text=f'1️⃣ Установите любое приложение по кнопкам ниже (или используйте любой другой Xray клиент)\n\n2️⃣ Скопируйте ключ подключения ниже в сообщении\n\n3️⃣ В приложении нажмите на *"+"* и выберите *"вставить"* или *"Добавить из буфера"*'
    text += f'\n\n4️⃣ *VPN Настроен и к готов работе*\n\n❗️*При настройке Hiddify установите регион "Другой"*\n\n⭕️*Если VPN подключается, но не работает в приложении Hiddify, перейдите в "Параметры конфигурации" установите в пункте "Режим работы" опцию "VPN сервис"* \n\n*КЛЮЧ ПОДКЛЮЧЕНИЯ:* \n\n`{link}`'

    builder.row(types.InlineKeyboardButton(text='Установить Hiddify ♠️', url='https://apps.microsoft.com/detail/9pdfnl3qv2s5'))

    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='set_slot'
    ))

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode='Markdown')
    await callback.answer()
    
@con_sub_router.callback_query(F.data == 'connect_macos')
async def connect_ios(callback: CallbackQuery):

    builder = InlineKeyboardBuilder()

    link = panel.link(callback.from_user.id)

    text=f'1️⃣ Установите любое приложение по кнопкам ниже (или используйте любой другой Xray клиент)\n\n2️⃣ Скопируйте ключ подключения ниже в сообщении\n\n3️⃣ В приложении нажмите на *"+"* и выберите *"вставить"* или *"Добавить из буфера"*'
    text += f'\n\n4️⃣ *VPN Настроен и к готов работе* \n\n*КЛЮЧ ПОДКЛЮЧЕНИЯ:* \n\n`{link}`'

    builder.row(types.InlineKeyboardButton(text='Установить v2RayTun ♠️', url='https://apps.apple.com/ru/app/v2raytun/id6476628951'))
    builder.row(types.InlineKeyboardButton(text='Установить V2Box ♦️', url='https://apps.apple.com/ru/app/v2box-v2ray-client/id6446814690'))

    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='set_slot'
    ))

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode='Markdown')
    await callback.answer()


@con_sub_router.callback_query(F.data == 'connect_android')
async def connect_ios(callback: CallbackQuery):

    builder = InlineKeyboardBuilder()

    link = panel.link(callback.from_user.id)

    text=f'1️⃣ Установите любое приложение по кнопкам ниже (или используйте любой другой Xray клиент)\n\n2️⃣ Скопируйте ключ подключения ниже в сообщении\n\n3️⃣ В приложении нажмите на *"+"* и выберите *"вставить"* или *"Добавить из буфера"*'
    text += f'\n\n4️⃣*VPN Настроен и к готов работе* \n\n*КЛЮЧ ПОДКЛЮЧЕНИЯ:* \n\n`{link}`'

    builder.row(types.InlineKeyboardButton(text='Установить Hiddify ♠️', url='https://play.google.com/store/apps/details?id=app.hiddify.com'))
    builder.row(types.InlineKeyboardButton(text='Установить V2Box ♦️', url='https://play.google.com/store/apps/details?id=dev.hexasoftware.v2box'))

    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='set_slot'
    ))

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode='Markdown')
    await callback.answer()

#connect_sub----------------------------------