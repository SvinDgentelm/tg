from aiogram.filters import BaseFilter
from aiogram.types import Message
from create_bot import database


class isAdminFilter(BaseFilter):
    async def __call__(self,message: Message):
        user = database.get_or_create(message.from_user.id, message.from_user.first_name)
        
        if user[3] == 1:
            return {'user': user}
        
        return False