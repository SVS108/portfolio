from aiogram import  F, types, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_place, orm_delete_place, orm_delete_place, orm_get_places, orm_change_place
from kbds.inline import get_callback_btns
from kbds.reply import place_KB
from common.states import AddPlace

place_id = 0

user_place_router = Router()
 
# Введем типы счетов
@user_place_router.message(F.text.lower() == "места")
async def account_type_types_cmd(message: types.Message, session: AsyncSession):
    places = await orm_get_places(session, message.from_user.id)
    if len(places) == 0:
        await message.answer("У вас пока нет мест.", reply_markup=place_KB)     
    else:
        await message.answer("У вас есть следующие места:", reply_markup=place_KB)
        for place in places:
            await message.answer(place.name, 
                                reply_markup=get_callback_btns(
                                        btns={
                                            "Удалить": f"deletepl_{place.id}",
                                            "Изменить": f"changepl_{place.id}",
                                        })
                                )       
        
@user_place_router.callback_query(F.data.startswith("changepl_"))
async def change_place_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    global place_id
    place_id = callback.data.split("_")[-1]
    await callback.message.answer("Введите название места:") 
    await state.set_state(AddPlace.name)

# Добавление нового места
@user_place_router.message(StateFilter(None), F.text.lower() == "добавить место")
async def add_place_cmd(message: types.Message, state: FSMContext):
    await message.answer("Введите название места:", reply_markup=types.ReplyKeyboardRemove()) 
    await state.set_state(AddPlace.name)

@user_place_router.message(AddPlace.name, F.text)
async def add_name(message: types.Message, session: AsyncSession, state: FSMContext):
    # проверка длины наименования счета
    global place_id

    if len(message.text) > 20:
        await message.answer("Название типа счета не должно превышать 20 символов. \n Введите заново")
        return
    
    data = {
        'user_id' : message.from_user.id,
        'name' : message.text     
     }
    
    if place_id == 0:
            await orm_add_place(session, data)
            await message.answer('Место "'+data['name']+'" успешно добавлено', reply_markup=place_KB)
    else:
        await orm_change_place(session, place_id, name=data['name'])
        await message.answer("Место изменено")
        place_id = 0
    await state.clear()

@user_place_router.callback_query(F.data.startswith("deletepl_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    place_id = callback.data.split("_")[-1]
    await orm_delete_place(session, int(place_id))

    await callback.answer("Место удалено")
    await callback.message.answer("Место удалено!")


    