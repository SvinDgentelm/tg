from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import types
from create_bot import database, panel, bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
from handlers.scheduler_func import add_slot_action

shop_router = Router()

#shop--------------------------------------------

@shop_router.callback_query(F.data=='shop_plan')
async def shop(callback: CallbackQuery):
    user = database.get_user(user_id=callback.from_user.id)
    builder = InlineKeyboardBuilder()

    if database.get_slot(user_id=user[2]) != None:

        builder.row(types.InlineKeyboardButton(text='Моя подписка',callback_data='user_slot_info'))
        
        text = 'Вы уже оформили подписку!'
    else:

        builder.row(types.InlineKeyboardButton(text='1 мес за 150 руб', callback_data='shop_chosen_1'))
        builder.row(types.InlineKeyboardButton(text='3 мес за 400 руб', callback_data='shop_chosen_2'))
        builder.row(types.InlineKeyboardButton(text='6 мес за 750 руб', callback_data='shop_chosen_3'))

        text = 'Выберите план подписки'

    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='main_menu'
    ))

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback.answer()

@shop_router.callback_query(F.data.startswith('shop_chosen_'))
async def slot_info(callback: CallbackQuery):
    
    plan_id = callback.data.split('_')[-1]
    plan = database.tariff_by_id(plan_id)

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='Перейти к оплате 💰',
        callback_data=f'payment_{plan_id}'
    ))

    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='shop_plan'
    ))

    await callback.message.edit_text(plan[3], reply_markup=builder.as_markup())
    await callback.answer()


@shop_router.callback_query(F.data.startswith('payment_'))
async def payment(callback: CallbackQuery):

    user = database.get_user(callback.from_user.id)

    plan_id = callback.data.split('_')[-1]

    plan = database.tariff_by_id(plan_id)

    price = plan[1]
    plan_text = plan[3]

    builder = InlineKeyboardBuilder()

    if int(price) > user[4]:
        text = f'💸 На вашем балансе недостаточно средств -- <b>{user[4]}</b> руб\n\nДля оплаты тарифа <b>{plan_text}</b>'
        builder.row(types.InlineKeyboardButton(text='Пополнить баланс 💰', callback_data='balance'))

    else:

        text = f'💎 У вас достаточно средств для оплаты тарифа <b>{plan_text}</b>'
        builder.row(types.InlineKeyboardButton(text='Подтверждаю покупку! 💰', callback_data=f'succes_payment_{plan_id}'))

    builder.row(types.InlineKeyboardButton(text='Отмена', callback_data='main_menu')) 

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback.answer()


@shop_router.callback_query(F.data.startswith('succes_payment_'))
async def succes_payment(callback: CallbackQuery):

    user = database.get_user(callback.from_user.id)

    plan = database.tariff_by_id(callback.data.split('_')[-1])

    database.update_user_balance(user_id=user[2], balance=user[4]- plan[1])

    days = plan[2]

    panel.add_client(user=user,days=days)
    key = panel.link(user_id=user[2])

    cur_date = datetime.today()
    next_payment = cur_date + timedelta(days=days)

    plan_id = plan[0]

    if plan[4] != None:
        plan_id = plan[4]


    slot = database.add_slot(user_id=user[2], plan=plan_id, key=key, next_payment=next_payment)
    add_slot_action(date=next_payment, slot_id=slot)

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='Моя подписка 🥸',
        callback_data='user_slot_info'
    ))
    builder.row(types.InlineKeyboardButton(text='Отмена', callback_data='main_menu'))

    admin = database.get_admin()
    await bot.send_message(chat_id=admin[2], text='new user!')

    await callback.message.edit_text(text="Спасибо за покупку", reply_markup=builder.as_markup())
    await callback.answer()

#shop--------------------------------------------------