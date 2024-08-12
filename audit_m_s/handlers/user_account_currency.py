from aiogram import  F, types, Router
from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Account_currency
from database.orm_query import orm_add_account_currency, orm_change_account_currency, orm_delete_account_currency, orm_get_account_currencies, orm_get_account_currency
from kbds.inline import get_callback_btns
from kbds.reply import account_KB, account_currency_KB
from common.states import AddAccountCurrency

user_account_currency_router = Router()

@user_account_currency_router.callback_query(StateFilter(None),F.data.startswith("changec_"))
async def change_account_type_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):

    account_currency_id = callback.data.split("_")[-1]
    account_currency_id_for_change = await orm_get_account_currency(session, int(account_currency_id))
    AddAccountCurrency.for_change=account_currency_id_for_change
    
    await callback.answer()
    await callback.message.answer("Введите название валюты:", reply_markup=types.ReplyKeyboardRemove()) 
    await state.set_state(AddAccountCurrency.name)

# Введем типы счетов
@user_account_currency_router.message(F.text.lower() == "валюты счетов")
async def account_type_types_cmd(message: types.Message, session: AsyncSession):
    await message.answer("У вас есть следующие валюты счетов:", reply_markup=account_currency_KB)
    for account_currency in await orm_get_account_currencies(session, message.from_user.id):
        await message.answer(account_currency.cod+' -> '+account_currency.name, 
                             reply_markup=get_callback_btns(
                                    btns={
                                        "Удалить": f"deletec_{account_currency.id}",
                                        "Изменить": f"changec_{account_currency.id}",
                                    })
                             )       
  
# Добавление новой валюты
@user_account_currency_router.message(StateFilter(None), F.text.lower() == "добавить валютy")
async def add_currency_cmd(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddAccountCurrency.name)

@user_account_currency_router.message(AddAccountCurrency.name, or_f(F.text, F.text=='.'))
async def add_currency_name_cmd(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(name=AddAccountCurrency.for_change.name)
    else:
        # проверка длины наименования счета
        if len(message.text) > 100:
            await message.answer("Название счета не должно превышать 100 символов. \n Введите заново")
            return
        await state.update_data(name=message.text)
    
    await message.answer("Введите код валюты")
    await state.set_state(AddAccountCurrency.cod)

@user_account_currency_router.message(AddAccountCurrency.cod, or_f(F.text, F.text=='.'))
async def add_currency_cod_cmd(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == '.':
        await state.update_data(cod=AddAccountCurrency.for_change.cod)
    # проверка длины типа счета
    else:
        if len(message.text) > 3:
            await message.answer("Код валюты не должен превышать 3 символа. \n Введите заново")
            return
        await state.update_data(cod=message.text)

    data = await state.get_data()

    if not AddAccountCurrency.for_change:
        await orm_add_account_currency(session, message.from_user.id, data)
        msg = "Валюта добавлена"
    else:
        await orm_change_account_currency(session, AddAccountCurrency.for_change.id, data)
        msg = "Валюта изменена"
    
    await message.answer(msg, reply_markup=account_KB)

    AddAccountCurrency.id_for_change = None
    await state.clear()

# Удаление существующего счета
@user_account_currency_router.message(F.text.lower() == "удалить валюту")
async def del_account_currency_cmd(message: types.Message, state: FSMContext):
    await message.answer("Выберите валюту для удаления:", reply_markup=types.ReplyKeyboardRemove())

@user_account_currency_router.callback_query(F.data.startswith("deletec_"))
async def delete_currency_callback(callback: types.CallbackQuery, session: AsyncSession):
    account_currency_id = callback.data.split("_")[-1]
    await orm_delete_account_currency(session, int(account_currency_id))

    await callback.answer("Валюта удалена")
    await callback.message.answer("Валюта удалена!")
