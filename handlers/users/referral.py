from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram import types
from create_bot import database, panel
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
from handlers.scheduler_func import add_slot_action


ref_router = Router()

@ref_router.callback_query(F.data=='referral_program')
async def main_ref(callback: CallbackQuery):

    builder = InlineKeyboardBuilder()

    user = database.get_user(user_id=callback.from_user.id)
    self_ref_link = user[5]

    text=f'❤️*Делитесь Prestige с близкими*❤️ \n\n💰Получайте награду💰\n*+150 руб на баланс вам*\n*+150 руб на баланс другу*\n\n👾Твоя ссылка👾\n`https://t.me/zhaba_blow_bot?start={self_ref_link}`\n\nБонусы начисляются после первой покупки приглашённого пользователя'

    builder.row(types.InlineKeyboardButton(
        text='Назад 🔙',
        callback_data='main_menu'
    ))

    await callback.message.edit_text(text=text,reply_markup=builder.as_markup(), parse_mode='Markdown')
    await callback.answer()