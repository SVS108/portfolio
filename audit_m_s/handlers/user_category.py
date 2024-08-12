from aiogram import  F, types, Router
from aiogram.filters import StateFilter, or_f
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Operation
from database.orm_query import orm_add_category, orm_delete_category, orm_get_categories, orm_change_category, orm_get_category
from kbds.inline import get_callback_btns
from kbds.reply import category_KB
from common.states import AddCategory

user_category_router = Router()
 
# Введем категории
@user_category_router.message(F.text.lower() == "категории")
async def categories_cmd(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session, message.from_user.id)
    sorted_cat = sorted(categories[4:], key=lambda x: x.category_type.name)

    if len(sorted_cat) == 0:
        await message.answer("У вас пока нет категорий:", reply_markup=category_KB)     
    else:  
        await message.answer("У вас есть следующие категории:", reply_markup=category_KB)
        for category in sorted_cat:
            category_line = category.category_type.value  + ": " + category.name
            await message.answer(category_line, 
                                reply_markup=get_callback_btns(
                                        btns={
                                            "Удалить": f"deletect_{category.id}",
                                            "Изменить": f"changect_{category.id}",
                                        })
                                )       
        
@user_category_router.callback_query(F.data.startswith("changect_"))
async def change_categpry_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    category_id = callback.data.split("_")[-1]
    category_for_change = await orm_get_category(session, int(category_id))
    AddCategory.for_change=category_for_change
    await callback.message.answer("Старый тип категории: "+AddCategory.for_change.category_type.value)    
    await callback.message.answer("Выберите тип категории:", 
                             reply_markup=get_callback_btns(
                                    btns={
                                        "Доходы": "earnings",
                                        "Расходы": "expenses",
                                    })
                             )       
    await state.set_state(AddCategory.category_type)

# Добавление новой категории
@user_category_router.message(StateFilter(None), F.text.lower() == "добавить категорию")
async def add_account_type_cmd(message: types.Message, state: FSMContext):
    if AddCategory.for_change:
        await message.answer("Старый тип категории: "+AddCategory.for_change.category_type.value)     
    await message.answer("Выберите тип категории:", 
                             reply_markup=get_callback_btns(
                                    btns={
                                        "Доходы": "earnings",
                                        "Расходы": "expenses",
                                    })
                             )       
    await state.set_state(AddCategory.category_type)

@user_category_router.callback_query(AddCategory.category_type, F.data.startswith("earnings"))
async def category_earnings_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.update_data(category_type=Operation.earnings)
    if AddCategory.for_change:
        await callback.message.answer("Старое название категории: "+AddCategory.for_change.name)     
    await callback.message.answer("Введите название категории:") 
    await state.set_state(AddCategory.name)

@user_category_router.callback_query(AddCategory.category_type, F.data.startswith("expenses"))
async def category_expenses_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.update_data(category_type=Operation.expenses)
    if AddCategory.for_change:
        await callback.message.answer("Старое название категории: "+AddCategory.for_change.name)     
    await callback.message.answer("Введите название категории:") 
    await state.set_state(AddCategory.name)

@user_category_router.message(AddCategory.name, or_f(F.text, F.text=='.'))
async def add_name(message: types.Message, session: AsyncSession, state: FSMContext):
    if message.text == '.':
        await state.update_data(name=AddCategory.for_change.name)
    else:
    # проверка длины наименования счета
        if len(message.text) > 50:
            await message.answer("Название категории не должно превышать 20 символов. \n Введите заново")
            return
        await state.update_data(name=message.text)

    state_dict = await state.get_data()

    data = {
        'user_id' : message.from_user.id,
        'category_type': state_dict['category_type'],
        'name' : state_dict['name']
     }
    
    if not AddCategory.for_change:
            await orm_add_category(session, data)
            await message.answer('Категория "'+data['name']+'" успешно добавлена', reply_markup=category_KB)
    else:
        await orm_change_category(session, AddCategory.for_change.id, data=data)
        await message.answer("Категория изменена")
        AddCategory.for_change = None
    await state.clear()

@user_category_router.callback_query(F.data.startswith("deletect_"))
async def delete_category_callback(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split("_")[-1]
    await orm_delete_category(session, int(category_id))

    await callback.answer("Категория удалена")
    await callback.message.answer("Категория удалена!")


    