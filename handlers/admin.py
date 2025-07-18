from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from create_bot import admins, database
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.is_admin import isAdminFilter
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from create_bot import bot

admin_router = Router()
admin_router.message.filter(isAdminFilter())
admin_router.callback_query.filter(isAdminFilter())




#----------ADMIN BOARD--------------------------------

@admin_router.message(Command('board'))
async def admin_board(message: Message):
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='Servers',
        callback_data='servers_1'
    ))

    builder.row(types.InlineKeyboardButton(
        text='Plans',
        callback_data='plans_1'
    ))

    await message.answer('Admin board', reply_markup=builder.as_markup())

@admin_router.callback_query(F.data=='admin_board')
async def admin_board(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='Servers',
        callback_data='servers_1'
    ))

    builder.row(types.InlineKeyboardButton(
        text='Plans',
        callback_data='plans_1'
    ))

    await callback.message.edit_text('Admin board', reply_markup=builder.as_markup())
    await callback.answer()

#---------------------------------------------

#------------PRICING PLANS--------------------

class AddPlanForm(StatesGroup):
    waiting_for_input = State()

class ChangePlanForm(StatesGroup):
    waiting_for_input = State()

class AddPlan(CallbackData, prefix='addplan'):
    name: str
    price: str
    connections: str
    trafic: str

class EditPlan(CallbackData, prefix='editplan'):
    id: str
    name: str
    price: str
    connections: str
    trafic: str


    ##-----------LIST OF PLANS----------------
@admin_router.callback_query(F.data.startswith('plans_'))
async def pricing_plans(callback: CallbackQuery):
    plans = database.get_all_plans()
    page = int(callback.data.split('_')[-1])

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='Add plan',
        callback_data='add_plan'
    ))


    view_plans = ''

    for plan in plans[(page-1)*3:(page-1) * 3 + 3]:

        view_plans += f'''    
        <i>{plan[1]}</i>
        <b>{plan[2]} rub/m</b>
        <b>{plan[3]} connections</b>
        <b>{plan[4]} Gbit/s</b>
        '''

        builder.row(types.InlineKeyboardButton(text=f'{plan[1]}', callback_data=f'manage_plan_{plan[0]}'))

    builder.row(types.InlineKeyboardButton(
        text='admin board',
        callback_data='admin_board'
    ))

    if page > 1 : 
        builder.add(types.InlineKeyboardButton(text=f'<<', callback_data=f'plans_{page-1}'))
    if page < len(plans)//3 + 1:
        builder.add(types.InlineKeyboardButton(text=f'>>', callback_data=f'plans_{page+1}'))


    builder.adjust(1,1,1,1,1,2)

    await callback.message.edit_text(f'Plans \n {page}\n {view_plans} \n', reply_markup=builder.as_markup())
    await callback.answer()
    ##--------------------------------




    ##--------ADDING PLANS------------
@admin_router.callback_query(F.data=='add_plan')
async def add_pricing_plans(callback: CallbackQuery, state: FSMContext):
    
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='Cancel',
        callback_data='plans_1'
    ))

    await callback.message.edit_text('Send plan`s data in format \n<b>Name   Price(rub/m)   Connections   Trafic(Gbit/s)</b>', reply_markup=builder.as_markup())
    await state.set_state(AddPlanForm.waiting_for_input)
    await callback.answer()

@admin_router.message(AddPlanForm.waiting_for_input)
async def info_princing_plans(message:Message, state: FSMContext):
    user_input = message.text.split()

    new_plan = {

        'name': user_input[0],
        'price': user_input[1],
        'connections': user_input[2],
        'trafic': user_input[3]

    }


    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text='Cancel', callback_data='add_plan'))
    builder.button(text='Confirm', callback_data=AddPlan(**new_plan, action='add'))


    await message.answer(f'''
    New plan`s data:
    Name: <b>{new_plan['name']}</b>
    Price: <b>{new_plan['price']} руб/мес</b>
    Connections: <b>{new_plan["connections"]}</b>
    Trafic: <b>{new_plan['trafic']} Gbit/s</b>
    ''',
    parse_mode=ParseMode.HTML,
    reply_markup=builder.as_markup())

    await state.clear()

@admin_router.callback_query(AddPlan.filter())
async def add_plans(callback: CallbackQuery, callback_data: AddPlan):
    

    database.add_plan(callback_data.name, callback_data.price, callback_data.connections, callback_data.trafic)

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='admin board',
        callback_data='admin_board'
    ))

    builder.row(types.InlineKeyboardButton(
        text='Add plan',
        callback_data='add_plan'
    ))

    await callback.message.edit_text('ADDING IS SUCCES', reply_markup=builder.as_markup())
    ##-----------------------------------






    ##---------MANAGE PLANS----------------
@admin_router.callback_query(F.data.startswith('manage_plan_'))
async def manage_plans(callback: CallbackQuery):
    plan_id = callback.data.split('_')[-1]

    plan = database.get_plan(plan_id)

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text='EDIT', callback_data=f'edit_plan_{plan_id}'))
    builder.row(types.InlineKeyboardButton(text='DELETE', callback_data=f'confirm_delete_plan_{plan_id}'))
    builder.row(types.InlineKeyboardButton(text='CANCEL', callback_data=f'plans_1'))

    await callback.message.edit_text(text=f'Manage \n<b>{plan[1]}   {plan[2]}(руб/мес)   {plan[3]}   {plan[4]}(Gbit/s)</b>', reply_markup=builder.as_markup())
    await callback.answer()



        ###----------DELETING PLANS---------------
@admin_router.callback_query(F.data.startswith('confirm_delete_plan_'))
async def confirm_delete_plan(callback: CallbackQuery):
    plan_id = callback.data.split('_')[-1]

    plan = database.get_plan(plan_id)

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='CONFIRM', callback_data=f'delete_plan_{plan_id}'))
    builder.row(types.InlineKeyboardButton(text='CANCEL', callback_data='plans_1'))

    await callback.message.edit_text(f'CONFIRM THE DELETION OF <b>{plan[1]}</b>', reply_markup=builder.as_markup())
    await callback.answer()

@admin_router.callback_query(F.data.startswith('delete_plan_'))
async def delete_plan(callback: CallbackQuery):
    plan_id = callback.data.split('_')[-1]

    database.del_plan(plan_id)
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='Back to plans', callback_data='plans_1'))

    await callback.message.edit_text(f'SUCCES DELETION', reply_markup=builder.as_markup())
    await callback.answer()
        ###---------------------------


        ###----------EDITING PLANS--------------
@admin_router.callback_query(F.data.startswith('edit_plan_'))
async def edit_plan(callback:CallbackQuery, state: FSMContext):
    plan_id = callback.data.split('_')[-1]

    plan=database.get_plan(plan_id)
    plan_data = f'{plan[0]} {plan[1]} {plan[2]} {plan[3]} {plan[4]}'

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='CANCEL', callback_data='plans_1'))

    await callback.message.edit_text(f"Send new plan info\n\nCopy current plan data in format\n\nid name price connections trafic\n`{plan_data}`\n\n:**Dont change format of data or id of plan**",
                                      parse_mode="Markdown", reply_markup=builder.as_markup())
    await state.set_state(ChangePlanForm.waiting_for_input) 
    await callback.answer()

@admin_router.message(ChangePlanForm.waiting_for_input)
async def info_editing_plan(message:Message, state: FSMContext):
    user_input = message.text.split()

    new_plan = {

        'id': user_input[0],
        'name': user_input[1],
        'price': user_input[2],
        'connections': user_input[3],
        'trafic': user_input[4]

    }


    builder = InlineKeyboardBuilder()

    builder.button(text='Confirm', callback_data=EditPlan(**new_plan))
    builder.add(types.InlineKeyboardButton(text='Cancel', callback_data=f"manage_plan_{new_plan['id']}"))


    await message.answer(f'''
    New plan`s data:
    Name: <b>{new_plan['name']}</b>
    Price: <b>{new_plan['price']} руб/мес</b>
    Connections: <b>{new_plan["connections"]}</b>
    Trafic: <b>{new_plan['trafic']} Gbit/s</b>
    ''',
    parse_mode=ParseMode.HTML,
    reply_markup=builder.as_markup())

    await state.clear()

@admin_router.callback_query(EditPlan.filter())
async def editing_plan(callback: CallbackQuery, callback_data: EditPlan):
    

    database.edit_plan(callback_data.id, callback_data.name, callback_data.price, callback_data.connections, callback_data.trafic)

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='admin board',
        callback_data='admin_board'
    ))

    builder.row(types.InlineKeyboardButton(
        text='Plans',
        callback_data='plans_1'
    ))

    await callback.message.edit_text('Changes are succes!', reply_markup=builder.as_markup())

        
        
        ###---------------------------
    ##---------------------------------------
#----------------------------------------------------


#---------SERVERS--------------------

class AddServerForm(StatesGroup):
    waiting_for_input = State()

class ChangeServerForm(StatesGroup):
    waiting_for_input = State()

class SendMessageForm(StatesGroup):
    waiting_for_input = State()

class AddServer(CallbackData, prefix='addserver'):
    name: str
    location: str
    ip: str
    status: str
    acceptable_conn: str
    cost: str

class EditServer(CallbackData, prefix='editserver'):
    id: str
    name: str
    location: str
    ip: str
    status: str
    acceptable_conn: str
    cost: str


    ##-----------LIST OF SERVERS----------------
@admin_router.callback_query(F.data.startswith('servers_'))
async def servers(callback: CallbackQuery):
    servers = database.get_all_servers()
    page = int(callback.data.split('_')[-1])

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='Add Server',
        callback_data='add_server'
    ))


    view_servers = ''

    for server in servers[(page-1)*3:(page-1) * 3 + 3]:

        view_servers += f'''    
        <i>{server[1]}</i>
        <b>{server[2]}</b>
        <b>{server[3]}</b>
        <b>{server[4]}</b>
        <b>{server[5]}</b>
        <b>{server[6]}</b>
        '''

        builder.row(types.InlineKeyboardButton(text=f'{server[1]}', callback_data=f'manage_server_{server[0]}'))

    builder.row(types.InlineKeyboardButton(
        text='admin board',
        callback_data='admin_board'
    ))

    if page > 1 : 
        builder.add(types.InlineKeyboardButton(text=f'<<', callback_data=f'servers_{page-1}'))
    if (page * 3) < len(servers):
        builder.add(types.InlineKeyboardButton(text=f'>>', callback_data=f'servers_{page+1}'))


    builder.adjust(1,1,1,1,1,2)

    await callback.message.edit_text(f'Servers \n {page}\n {view_servers} \n', reply_markup=builder.as_markup())
    await callback.answer()
    ##--------------------------------




    ##--------ADDING SERVERS------------

@admin_router.message(Command('add_balance'))
async def add_balance(message: Message, command: CommandObject):
    
    args = command.args

    user_id=args.split()[0]
    sum=int(args.split()[1])

    database.raise_user_balance(user_id=user_id, sum=sum)

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='OK', callback_data='del_message'))

    await bot.send_message(chat_id=user_id, text=f"Ваш баланс пополнен на {sum} руб", reply_markup=builder.as_markup())

@admin_router.message(Command('add_balance_byname'))
async def add_balance(message: Message, command: CommandObject):
    
    args = command.args

    username=args.split()[0]
    sum=int(args.split()[1])

    user_id = database.raise_by_username(username=username, sum=sum)

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='OK', callback_data='del_message'))

    await bot.send_message(chat_id=user_id, text=f"Ваш баланс пополнен на {sum} руб", reply_markup=builder.as_markup())


@admin_router.callback_query(F.data=='add_server')
async def add_servers(callback: CallbackQuery, state: FSMContext):
    
    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='Cancel',
        callback_data='servers_1'
    ))

    await callback.message.edit_text('Send server data in format \n<b>Name   Location   IP   Status   Acceptable_connectsions Cost</b>', reply_markup=builder.as_markup())
    await state.set_state(AddServerForm.waiting_for_input)
    await callback.answer()

@admin_router.message(AddServerForm.waiting_for_input)
async def info_server(message:Message, state: FSMContext):
    user_input = message.text.split()

    new_server = {

        'name': user_input[0],
        'location': user_input[1],
        'ip': user_input[2],
        'status': user_input[3],
        'acceptable_conn': user_input[4],
        'cost': user_input[5]


    }


    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text='Cancel', callback_data='add_server'))
    builder.button(text='Confirm', callback_data=AddServer(**new_server))


    await message.answer(f'''
    New server data:
    Name: <b>{new_server['name']}</b>
    Location: <b>{new_server['location']}</b>
    IP: <b>{new_server["ip"]}</b>
    Status: <b>{new_server['status']}</b>
    Acceptable connectuions: <b>{new_server['acceptable_conn']}</b>
    Cost: <b>{new_server['cost']}</b>
    ''',
    parse_mode=ParseMode.HTML,
    reply_markup=builder.as_markup())

    await state.clear()

@admin_router.callback_query(AddServer.filter())
async def add_server(callback: CallbackQuery, callback_data: AddServer):
    

    database.add_server(callback_data.name, callback_data.location, callback_data.ip, callback_data.status, callback_data.acceptable_conn, callback_data.acceptable_conn)

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='admin board',
        callback_data='admin_board'
    ))

    builder.row(types.InlineKeyboardButton(
        text='Servers',
        callback_data='servers_1'
    ))

    await callback.message.edit_text('ADDING SERVER IS SUCCES', reply_markup=builder.as_markup())
    ##-----------------------------------






    ##---------MANAGE SERVERS----------------
@admin_router.callback_query(F.data.startswith('manage_server_'))
async def manage_servers(callback: CallbackQuery):
    server_id = callback.data.split('_')[-1]

    server = database.get_server(server_id)

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(text='EDIT', callback_data=f'edit_server_{server_id}'))
    builder.row(types.InlineKeyboardButton(text='DELETE', callback_data=f'confirm_delete_server_{server_id}'))
    builder.row(types.InlineKeyboardButton(text='CANCEL', callback_data=f'servers_1'))

    await callback.message.edit_text(text=f'Manage \n<b>{server[1]}   {server[2]}   {server[3]}   {server[4]} {server[5]} {server[6]}</b>', reply_markup=builder.as_markup())
    await callback.answer()



        ###----------DELETING SERVERS---------------
@admin_router.callback_query(F.data.startswith('confirm_delete_server_'))
async def confirm_delete_server(callback: CallbackQuery):
    server_id = callback.data.split('_')[-1]

    server = database.get_server(server_id)

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='CONFIRM', callback_data=f'delete_server_{server_id}'))
    builder.row(types.InlineKeyboardButton(text='CANCEL', callback_data='servers_1'))

    await callback.message.edit_text(f'CONFIRM THE DELETION OF <b>{server[1]}</b>', reply_markup=builder.as_markup())
    await callback.answer()

@admin_router.callback_query(F.data.startswith('delete_server_'))
async def delete_server(callback: CallbackQuery):
    server_id = callback.data.split('_')[-1]

    database.del_server(server_id)
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='Back to servers', callback_data='servers_1'))

    await callback.message.edit_text(f'SUCCES DELETION', reply_markup=builder.as_markup())
    await callback.answer()
        ###---------------------------


        ###----------EDITING SERVER--------------

@admin_router.message(Command('send_message'))
async def send_admin_message(message:Message, state:FSMContext):

    await state.set_state(SendMessageForm.waiting_for_input)

@admin_router.message(SendMessageForm.waiting_for_input)
async def get_send_admin_message(message: Message, state: FSMContext):
    text = message.text

    OK = InlineKeyboardBuilder()
    OK.row(types.InlineKeyboardButton(text='OK', callback_data='del_message'))

    users = database.get_slots()

    for user in users:
        await bot.send_message(text=text, reply_markup=OK.as_markup(), chat_id=user[0])
    await state.clear()

@admin_router.callback_query(F.data.startswith('edit_server_'))
async def edit_server(callback:CallbackQuery, state: FSMContext):
    server_id = callback.data.split('_')[-1]

    server=database.get_server(server_id)
    server_data = f'{server[0]} {server[1]} {server[2]} {server[3]} {server[4]} {server[5]} {server[6]}'

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text='CANCEL', callback_data='servers_1'))

    await callback.message.edit_text(f"Send new server info\n\nCopy current plan data in format\n\nid name location ip status acceptedConnections cost\n`{server_data}`\n\n**Dont change format of data or id of plan**",
                                      parse_mode="Markdown", reply_markup=builder.as_markup())
    await state.set_state(ChangeServerForm.waiting_for_input) 
    await callback.answer()

@admin_router.message(ChangeServerForm.waiting_for_input)
async def info_editing_server(message:Message, state: FSMContext):
    user_input = message.text.split()

    new_server = {

        'id': user_input[0],
        'name': user_input[1],
        'location': user_input[2],
        'ip': user_input[3],
        'status': user_input[4],
        'acceptable_conn': user_input[5]

    }


    builder = InlineKeyboardBuilder()

    builder.button(text='Confirm', callback_data=EditServer(**new_server))
    builder.add(types.InlineKeyboardButton(text='Cancel', callback_data=f"manage_server_{new_server['id']}"))


    await message.answer(f'''
    New server data:
    Name: <b>{new_server['name']}</b>
    Location: <b>{new_server['location']}</b>
    IP: <b>{new_server["ip"]}</b>
    Status: <b>{new_server['status']}</b>
    Acceptable connectuions: <b>{new_server['acceptable_conn']}</b>
    ''',
    parse_mode=ParseMode.HTML,
    reply_markup=builder.as_markup())

    await state.clear()

@admin_router.callback_query(EditServer.filter())
async def editing_server(callback: CallbackQuery, callback_data: EditServer):
    

    database.edit_server(callback_data.id, callback_data.name, callback_data.location, callback_data.ip, callback_data.status, callback_data.acceptable_conn)

    builder = InlineKeyboardBuilder()

    builder.row(types.InlineKeyboardButton(
        text='admin board',
        callback_data='admin_board'
    ))

    builder.row(types.InlineKeyboardButton(
        text='Servers',
        callback_data='servers_1'
    ))

    await callback.message.edit_text('Changes are succes!', reply_markup=builder.as_markup())

        
        
        ###---------------------------
    ##---------------------------------------

    ##--------PLANS TO SERVERS---------------
