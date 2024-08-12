from aiogram import  F, types, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_account_type, orm_delete_account_types, orm_get_account_types, orm_change_account_types
from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard, account_type_KB
from common.states import AddAccountType

account_type_id = 0

user_account_type_router = Router()
 
# Введем типы счетов
@user_account_type_router.message(F.text.lower() == "типы счетов")
async def account_type_types_cmd(message: types.Message, session: AsyncSession):
    await message.answer("У вас есть следующие типы счетов:", reply_markup=account_type_KB)
    for account_type in await orm_get_account_types(session, message.from_user.id):
        await message.answer(account_type.name, 
                             reply_markup=get_callback_btns(
                                    btns={
                                        "Удалить": f"delete_{account_type.id}",
                                        "Изменить": f"change_{account_type.id}",
                                    })
                             )       
        
@user_account_type_router.callback_query(F.data.startswith("change_"))
async def change_account_type_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    global account_type_id
    account_type_id = callback.data.split("_")[-1]
    await callback.message.answer("Введите тип счета:") 
    await state.set_state(AddAccountType.name)

# Добавление нового счета
@user_account_type_router.message(StateFilter(None), F.text.lower() == "добавить тип счета")
async def add_account_type_cmd(message: types.Message, state: FSMContext):
    await message.answer("Введите тип счета:", reply_markup=types.ReplyKeyboardRemove()) 
    await state.set_state(AddAccountType.name)

@user_account_type_router.message(AddAccountType.name, F.text)
async def add_name(message: types.Message, session: AsyncSession, state: FSMContext):
    # проверка длины наименования счета
    global account_type_id

    if len(message.text) > 20:
        await message.answer("Название типа счета не должно превышать 20 символов. \n Введите заново")
        return
    
    data = {
        'user_id' : message.from_user.id,
        'name' : message.text     
     }
    
    if account_type_id == 0:
            await orm_add_account_type(session, data)
            await message.answer('Тип счета "'+data['name']+'" успешно добавлен', reply_markup=account_type_KB)
    else:
        await orm_change_account_types(session, account_type_id, name=message.text)
        await message.answer("Тип счета изменен")
        account_type_id = 0
    await state.clear()

@user_account_type_router.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    account_type_id = callback.data.split("_")[-1]
    await orm_delete_account_types(session, int(account_type_id))

    await callback.answer("Тип счета удален")
    await callback.message.answer("Тип счета удален!")


    