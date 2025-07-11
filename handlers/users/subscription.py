from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import types
from create_bot import database, panel
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime


sub_router = Router()

#subscription----------------------------------

@sub_router.callback_query(F.data.startswith('user_slot_info'))
async def slot_info(callback: CallbackQuery):
    
    slot = database.get_slot(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    
    if slot == None:
        
        builder.row(types.InlineKeyboardButton(
            text='Купить подписку',
            callback_data='shop_plan'
        ))

        builder.row(types.InlineKeyboardButton(
            text='Назад 🔙',
            callback_data='main_menu'
        ))

        await callback.message.edit_text(text='У вас ещё нет купленной подписки', reply_markup=builder.as_markup())
        await callback.answer()

    else:

        statuses = {
            '1': 'Активная 💎',
            '2': 'Приостановлена 😴',
            '3': 'Ожидает оплаты 😵‍💫'
        }

        plan = database.tariff_by_id(str(slot[3]))
        status = statuses[str(slot[2])]

        creation_date = datetime.strptime(slot[4], "%Y-%m-%d %H:%M:%S.%f").strftime("%d.%m.%Y")
        next_payment_date = datetime.strptime(slot[5], "%Y-%m-%d %H:%M:%S.%f").strftime("%d.%m.%Y")

        text=f'🎖Ваш тариф: <b>{plan[3]}</b>\n\n🤌Статус подписки: <b>{status}</b>\n\n🗓Дата подписки: <b>{creation_date}</b>\n\n🗓Ожидаемсая дата продления: <b>{next_payment_date}</b>'

        builder.row(types.InlineKeyboardButton(text='Подключить VPN 👾', callback_data=f'set_slot'))
        
        if slot[2]=='1':
            builder.row(types.InlineKeyboardButton(text='Изменить тариф подписки ✍️', callback_data=f'change_plan'))
            builder.row(types.InlineKeyboardButton(text='Приостановить подписку 😵', callback_data=f'aprove_unsub_slot_{slot[0]}'))
        elif slot[2]=='2':
            builder.row(types.InlineKeyboardButton(text='Возобновить подписку 🦾', callback_data=f'aprove_resub_slot_{slot[0]}'))



        builder.row(types.InlineKeyboardButton(
            text='Назад 🔙',
            callback_data='main_menu'
        ))

        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        await callback.answer()


@sub_router.callback_query(F.data.startswith('aprove_unsub_slot_'))
async def aprove_unsub_slot(callback: CallbackQuery):

    slot_id = callback.data.split('_')[-1]

    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text='Нет🟢', callback_data=f'user_slot_info_{slot_id}'))
    builder.add(types.InlineKeyboardButton(text='Да🔴', callback_data=f'unsub_slot_{slot_id}'))

    await callback.message.edit_text('\n<b>Вы уверены, что хотите приостановить подписку?</b>😵\n', reply_markup=builder.as_markup())
    await callback.answer()

@sub_router.callback_query(F.data.startswith('unsub_slot_'))
async def unsub_slot(callback: CallbackQuery):

    slot_id = callback.data.split('_')[-1]
    slot = database.get_slot(callback.from_user.id)
    
    database.unsub_slot(slot_id)

    next_payment_date = datetime.strptime(slot[5], "%Y-%m-%d %H:%M:%S.%f").strftime("%d.%m.%Y")

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text='К подписке 👾', callback_data=f'user_slot_info'))
    builder.row(types.InlineKeyboardButton(text='На главную 🏠',callback_data='main_menu'))

    await callback.message.edit_text(f'😔<b>Подписка приостановлена</b>\n\nVPN будет доступен до даты следующей оплаты\n\n🗓<b>{next_payment_date}</b>\n\n😵‍💫 <b>После даты следующей оплаты подписка будет полностью остановлена</b>',
                                     reply_markup=builder.as_markup())
    await callback.answer()
    

@sub_router.callback_query(F.data.startswith('aprove_resub_slot_'))
async def aprove_resub_slot(callback: CallbackQuery):
    
    slot_id = callback.data.split('_')[-1]

    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text='Да🟢', callback_data=f'resub_slot_{slot_id}'))
    builder.add(types.InlineKeyboardButton(text='Нет🔴', callback_data=f'user_slot_info_{slot_id}'))

    await callback.message.edit_text('\n<b>Вы уверены, что хотите возобновить подписку?</b>🥰\n', reply_markup=builder.as_markup())
    await callback.answer()

@sub_router.callback_query(F.data.startswith('resub_slot_'))
async def resub_slot(callback: CallbackQuery):
    
    slot_id = callback.data.split('_')[-1]
    slot = database.get_slot(callback.from_user.id)
    
    database.resub_slot(slot_id)

    next_payment_date = datetime.strptime(slot[5], "%Y-%m-%d %H:%M:%S.%f").strftime("%d.%m.%Y")

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text='К подписке 👾', callback_data=f'user_slot_info'))
    builder.row(types.InlineKeyboardButton(text='На главную 🏠',callback_data='main_menu'))

    await callback.message.edit_text(f'\n<b>Подписка успешно восстановлена</b>🤩\n',reply_markup=builder.as_markup())
    await callback.answer()

@sub_router.callback_query(F.data=='bon')
async def bon(callback: CallbackQuery):

    panel.updateClientDate(days=1, user_id=callback.from_user.id)
    await callback.answer()


@sub_router.callback_query(F.data=='change_plan')
async def change_plan(callback: CallbackQuery):
    
    user_id = callback.from_user.id
    user = database.get_user(user_id)

    slot = database.get_slot(user_id)

    builder = InlineKeyboardBuilder()

    plans = {
        '1': ('1 мес', 150),
        '2': ('3 мес', 400),
        '3': ('6 мес', 750)
    }
    
    plan = plans[str(slot[3])]

    for plan_id in plans:

        if plan != plans[plan_id]:
            builder.row(types.InlineKeyboardButton(text=f'{plans[plan_id][0]} за {plans[plan_id][1]} руб', callback_data=f'change_plan_on_{plan_id}'))

    builder.row(types.InlineKeyboardButton(text='Назад 🔙',callback_data='user_slot_info'))

    text = f'🎖Ваш тариф: <b>{plan[0]}</b> за <i>{plan[1]} руб</i>\n\nДругие возвожные тарифы:'

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback.answer()

@sub_router.callback_query(F.data.startswith('change_plan_on_'))
async def aprv_change_plan(callback: CallbackQuery):

    new_plan_id = callback.data.split('_')[-1]

    new_plan = database.tariff_by_id(new_plan_id)

    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text='Да🟢', callback_data=f'plan_changed_{new_plan_id}'))
    builder.add(types.InlineKeyboardButton(text='Нет🔴', callback_data='user_slot_info'))
    
    text = f'❓ Изменить тариф на {new_plan[3]} ❓'

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback.answer()

@sub_router.callback_query(F.data.startswith('plan_changed_'))
async def changing_plan(callback: CallbackQuery):

    user_id = callback.from_user.id
    plan_id = callback.data.split('_')[-1]

    database.change_plan_by_user(user_id=user_id, plan_id=plan_id)

    text=f'🎖<b>Вы изменили тариф</b>🎖\n\n🗓<i>Изменения ввойдут в силу после следущего списания</i>'

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='Назад к подписке🔙',callback_data='user_slot_info'))
    builder.row(types.InlineKeyboardButton(text='На главную 🏠',callback_data='main_menu'))

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback.answer()

#subscration----------------------------------
