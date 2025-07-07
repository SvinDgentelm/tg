from aiogram import Router, F
from aiogram.filters import CommandStart, Command,CommandObject
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram import types
from create_bot import admins, database
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):

    args = command.args

    if args:
        print(args)

    user = database.get_or_create(message.from_user.id, message.from_user.first_name)
    if user:
        await message.answer(f'Hello, {user[1]}')
        

@start_router.message(Command('check'))
async def cmd_check(message: Message):
    if message.from_user.id in admins:
        database.add_user(message.from_user.first_name, message.from_user.id)
        await message.answer('GODem')
    else:
        await message.answer('газу!!')

@start_router.message(Command('keyboard'))
async def keyboard(message:Message):
    kb = [
        [
        KeyboardButton(text='key1'),
        KeyboardButton(text='key2')
        ],
        [KeyboardButton(text='bb')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder='ok&')
    await message.answer('ok', reply_markup=keyboard)


@start_router.message(F.text.lower() == 'bb')
async def bb (message: Message):
    await message.answer('bb', reply_markup=types.ReplyKeyboardRemove())

@start_router.message(Command('inline'))
async def inline(message:Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='text_button',
        callback_data='good'
    ))

    await message.answer('Tikay', reply_markup=builder.as_markup())

@start_router.callback_query(F.data == 'good')
async def send_callback(callback: types.CallbackQuery):
    await callback.message.answer('10000')
    await callback.answer()

@start_router.message(F.text == '/chupep')
async def cmd_chupep(message: Message):
    await message.answer('чюпеп')