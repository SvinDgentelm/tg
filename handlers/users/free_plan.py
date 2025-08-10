from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import types
from create_bot import database, panel
from aiogram.utils.keyboard import InlineKeyboardBuilder

free_plan = Router()

@free_plan.callback_query(F.data == 'free_plan')
async def main_free_plan(callback: CallbackQuery):

    builder = InlineKeyboardBuilder()

    text = "🎁 **Пробная подписка на 7 дней!**\nДалее 150руб/мес"

    builder.row(types.InlineKeyboardButton(
        text='Подключить vpn 👾',
        callback_data='succes_payment_4'
    ))


    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='main_menu'
    ))
    await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode='Markdown')
    await callback.answer()
