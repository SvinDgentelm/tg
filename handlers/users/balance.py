from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from create_bot import database, bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

from decouple import config
import requests

balance_router = Router()

#balance--------------------------------------

@balance_router.callback_query(F.data == 'balance')
async def view_balance(callback: types.CallbackQuery):
    user = database.get_or_create(user_id=callback.from_user.id, username=callback.from_user.first_name)
    slot = database.get_slot(user[2])

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='Пополнить 💳',
        callback_data='topup'
    ))

    if slot == None:
        
        builder.row(types.InlineKeyboardButton(
            text='Подключить VPN 💎',
            callback_data='shop_plan'
        ))


    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='main_menu'
    ))

    await callback.message.edit_text(f'💵<b>Ваш баланс:</b>  <i>{user[4]} руб</i>', reply_markup=builder.as_markup())
    await callback.answer()

@balance_router.callback_query(F.data == 'topup')
async def choose_topup(callback: CallbackQuery):

    user = database.get_user(callback.from_user.id)

    builder = InlineKeyboardBuilder()  

    builder.row(types.InlineKeyboardButton(text='Пополнить на 200 руб 💵', callback_data='topup_200'))
    builder.row(types.InlineKeyboardButton(text='Пополнить на 600 руб 💴', callback_data='topup_600'))
    builder.row(types.InlineKeyboardButton(text='Пополнить на 900 руб 💶', callback_data='topup_900'))

    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='balance'
    ))

    text='⬇️Выберите сумму пополнения⬇️'

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback.answer()

@balance_router.callback_query(F.data.startswith('topup_'))
async def choose_payment(callback: CallbackQuery):

    amount = callback.data.split('_')[-1]

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text=f'Оплатить звездами телеграмм {int(amount)//2}⭐️', callback_data=f'pay_by_stars_{amount}'))
    builder.row(types.InlineKeyboardButton(text=f'Оплатить крпитовалютой {int(amount)} руб', callback_data=f'pay_by_crypto_{amount}'))

    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='topup'
    ))

    await callback.message.edit_text(text='⬇️Выберите тип оплаты⬇️', reply_markup=builder.as_markup())
    await callback.answer()

@balance_router.callback_query(F.data.startswith('cancel_by_stars_'))
async def cancel_by_stars(callback: CallbackQuery):

    amount = callback.data.split('_')[-1]

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text=f'Оплатить звездами телеграмм {int(amount)//2}⭐️', callback_data=f'pay_by_stars_{amount}'))
    builder.row(types.InlineKeyboardButton(text=f'Оплатить крпитовалютой {int(amount)} руб', callback_data=f'pay_by_crypto_{amount}'))

    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='topup'
    ))

    await callback.message.answer(text='⬇️Выберите тип оплаты⬇️', reply_markup=builder.as_markup())
    await callback.answer()

@balance_router.callback_query(F.data.startswith('pay_by_stars_'))
async def pay_by_stars(callback: CallbackQuery):

    amount = int(callback.data.split('_')[-1]) // 2

    builder = InlineKeyboardBuilder()

    builder.button(text=f'Оплатить {amount} XTR', pay=True)
    builder.button(text=f'Отменить', callback_data=f'cancel_by_stars_{amount*2}')

    builder.adjust(1)

    prices = [types.LabeledPrice(label="XTR", amount=amount)]

    await callback.message.answer_invoice(
        title=f'Пополнение счёта',
        prices=prices,
        provider_token='',
        description=f'Пополнение счёта на {amount*2} руб',
        payload=f"{amount}",
        currency="XTR",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@balance_router.callback_query(F.data.startswith('pay_by_crypto'))
async def pay_by_crypto(callback: CallbackQuery):

    user_id = callback.from_user.id

    amount = callback.data.split('_')[-1]
    crypto_url = "https://pay.crypt.bot/api/createInvoice"
    crypto_token = config('CRYPTO_TOKEN')

    user_id = callback.from_user.id

    headers = {
        "Crypto-Pay-API-Token": crypto_token,
        "Content-Type": "application/json"
    }

    data = {
        'currency_type': 'fiat',
        'fiat': "RUB",
        'accepted_assets': "USDT",
        'amount': amount,
        'expires_in': 600,
        'payload': f'{user_id}_{amount}',
        'description': f'Top up on {amount} rub'

    }

    response = requests.post(crypto_url, json=data, headers=headers)
    invoice = response.json()

    invoice_id = invoice['result']['invoice_id']
    payment_url = invoice['result']['mini_app_invoice_url']

    database.add_invoice(user_id=user_id, invoice_id=invoice_id, amount=amount)

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='Оплатить🟢', url=payment_url))
    builder.row(types.InlineKeyboardButton(text='Отмена🔴', callback_data=f'cancel_by_crypto_{invoice_id}'))

    await callback.message.edit_text(text='Оплатите счёт в течение 15 мин', reply_markup=builder.as_markup())
    await callback.answer()

@balance_router.callback_query(F.data.startswith('cancel_by_crypto_'))
async def cancel_by_crypto(callback: CallbackQuery):

    invoice_id = callback.data.split('_')[-1]
    database.del_invoice(invoice_id=invoice_id)

    await choose_topup(callback)


@balance_router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: types.PreCheckoutQuery,
):
    await pre_checkout_query.answer(ok=True)

@balance_router.message(F.successful_payment)
async def successful_payment(message: Message):

    user = database.get_user(message.from_user.id)
    amount = int(message.successful_payment.invoice_payload) * 2
    id = message.successful_payment.telegram_payment_charge_id

    database.update_user_balance(user_id=user[2], balance=int(user[4]) + amount)

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='Назад 🔙',callback_data='balance'))

    text=f'🎉 Оплата прошла усешно! \n\n💰 <b>{amount} руб</b> зачислены на баланс \n\n💳 id транзакции: \n <code>{id}</code>'

    await message.answer(text=text, reply_markup=builder.as_markup())

    if user[6] != None and user[6] != 'done':
        
        sum = database.tariff_by_id(id=1)[1]

        database.raise_user_balance(user_id=message.from_user.id, sum=sum)

        user_friend = database.get_by_ref(ref_link=user[6])
        database.raise_user_balance(user_id=user_friend[2], sum=sum)

        database.paid_ref(user_id=message.from_user.id)

        OK = InlineKeyboardBuilder()
        OK.row(types.InlineKeyboardButton(text='OK', callback_data='del_message'))

        await bot.send_message(chat_id=message.from_user.id, text=f'Вам начислен бонус {sum} руб за реферальную систему!',
                               reply_markup=OK.as_markup())
        
        await bot.send_message(chat_id=user_friend[2], text=f'Вам начислен бонус {sum} руб за реферальную систему!',
                               reply_markup=OK.as_markup())





@balance_router.message(Command('refund'))
async def refund(message: Message, command: CommandObject):
    
    transaction_id = command.args
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='ok',callback_data='del_message'))
    
    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id
        )
        await message.answer(
            text='refunded', reply_markup=builder.as_markup()
        )
    except TelegramBadRequest as error:
        if "CHARGE_NOT_FOUND" in error.message:
            text = "refund-code-not-found"
        elif "CHARGE_ALREADY_REFUNDED" in error.message:
            text = "refund-already-refunded"
        else:
            # При всех остальных ошибках – такой же текст,
            # как и в первом случае
            text = "refund-code-not-found"
        await message.answer(text)


#balance-------------------------------------------------