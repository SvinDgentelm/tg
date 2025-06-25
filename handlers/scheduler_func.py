from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from handlers.users.main_menu import database,scheduler,bot,panel
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.is_admin import isAdminFilter
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from datetime import datetime, timedelta

import json
from decouple import config
import requests

async def slot_action(slot_id: int):
    
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text='OK', callback_data='del_message'))

    slot = database.get_slot_byid(slot_id)

    user = database.get_user(slot[1])

    slot_status = slot[2]

    plan = database.tariff_by_id(str(slot[3]))

    price = plan[1]
    days = plan[2]

    if slot_status == '1':
        
        if int(user[4]) >= price:
            
            next_payment = datetime.strptime(slot[5], "%Y-%m-%d %H:%M:%S.%f") + timedelta(days=days)

            database.update_slot_payment(slot_id=slot_id, next_payment=next_payment)
            database.update_user_balance(user_id=slot[1], balance=int(user[4]) - price)

            scheduler.add_job(
                slot_action,
                trigger='date',
                run_date=next_payment,
                args=[slot_id],
                misfire_grace_time=None,
                id=f'{next_payment}_{slot_id}',
            )

            panel.updateClientDate(days=days, user_id=user[2])

            await bot.send_message(user[2], f'Подписка на была успешно продлена\nВаш баланс:  <b>{int(user[4]) - price}</b>\nДата следующего продления:  <b>{next_payment.strftime("%d.%m.%Y")}</b>',
                                   reply_markup=builder.as_markup())
        
        else:

            cur_date = datetime.today()
            next_payment = cur_date + timedelta(days=3)
            
            scheduler.add_job(
                slot_action,
                trigger='date',
                run_date=next_payment,
                args=[slot_id],
                misfire_grace_time=None,
                id=f'{next_payment}_{slot_id}',
            )
            
            database.unpaid_slot(slot_id=slot_id)
            await bot.send_message(user[2], f'Не удалось оплатить подписку стоимостью <b>{price}</b>\n<b>{next_payment.strftime("%d.%m.%Y")}</b> будет произведена повторная попытка оплаты',
                                   reply_markup=builder.as_markup())
    
    elif slot_status == '2':

        database.del_slot(slot_id=slot_id)
        await bot.send_message(user[2], f'Действие подписки было прекращено', reply_markup=builder.as_markup())

    elif slot_status == '3':

        if int(user[4]) >= price:
            
            database.paid_slot(slot_id=slot_id)

            next_payment = datetime.strptime(slot[5], "%Y-%m-%d %H:%M:%S.%f") + timedelta(days=days)

            database.update_slot_payment(slot_id=slot_id, next_payment=next_payment)
            database.update_user_balance(user_id=slot[1], balance=int(user[4]) - price)

            scheduler.add_job(
                slot_action,
                trigger='date',
                run_date=next_payment,
                args=[slot_id],
                misfire_grace_time=None,
                id=f'{next_payment}_{slot_id}',
            )

            panel.updateClientDate(days=days, user_id=user[2])
            
            await bot.send_message(user[2], f'Подписка была успешно продлена\nВаш баланс:  <b>{int(user[4]) - price}</b>\nДата следующего продления:  <b>{next_payment.strftime("%d.%m.%Y")}</b>',
                                   reply_markup=builder.as_markup())

        else:
            
            database.del_slot(slot_id=slot_id)
            await bot.send_message(user[2], f'Действие подписки было прекращено', reply_markup=builder.as_markup())

async def check_invoices():

    active_invoices = database.get_invoices()

    for active_invoice in active_invoices:

        invoice_id = active_invoice[2]
        user_id = active_invoice[1]
        amount = active_invoice[3]

        crypto_url = "https://pay.crypt.bot/api/getInvoices"
        crypto_token = config('CRYPTO_TOKEN')

        data = {'invoice_ids': invoice_id}
        headers = {
            "Crypto-Pay-API-Token": crypto_token
        }

        response = requests.post(crypto_url, json=data, headers=headers)
        invoice = response.json()['result']['items'][0]

        invoice_status = invoice['status']

        builder = InlineKeyboardBuilder()

        if invoice_status == 'paid':

            database.raise_user_balance(user_id=user_id, sum=amount)
            database.del_invoice(invoice_id=invoice_id)

            builder.row(types.InlineKeyboardButton(text='OK', callback_data='balance'))

            await bot.send_message(user_id, text='Счёт оплачен, <b>средства зачилены на баланс</b>🟢', reply_markup=builder.as_markup())
        
        elif invoice_status == 'expired':

            database.del_invoice(invoice_id=invoice_id)

            builder.row(types.InlineKeyboardButton(text='OK', callback_data='balance'))

            await bot.send_message(user_id, text='Время действия счёта истекло, пожалуйста попробуйте ещё раз⭕️', reply_markup=builder.as_markup())

#scheduler.add_job(check_invoices, "interval", seconds=60)

def add_slot_action(date, slot_id):

    date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S.%f")

    scheduler.add_job(
        slot_action,
        trigger='date',
        run_date=date,
        args=[slot_id],
        misfire_grace_time=None,
        id=f'{date}_{slot_id}',
    )

