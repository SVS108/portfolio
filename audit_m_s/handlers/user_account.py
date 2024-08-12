from aiogram import  F, types, Router
from aiogram.filters import or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Account
from kbds.reply import account_KB
from common.states import AddAccount
from database.orm_query import orm_add_account, orm_change_account, orm_delete_account, orm_get_account, \
                               orm_get_account_currencies, \
                               orm_get_account_currency, orm_get_account_type, \
                               orm_get_account_types, orm_get_accounts
from kbds.inline import get_callback_btns

user_account_router = Router()

@user_account_router.message((F.text.lower() == 'счета'))
async def accounts_cmd(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=account_KB)

# Посмотрим счета: сформируем инлайн-кнопки с названиями счетов
@user_account_router.message(F.text.lower() == "посмотреть счета")
async def get_accounts_cmd(message: types.Message, state: FSMContext, session: AsyncSession):
    accounts = await orm_get_accounts(session, message.from_user.id)
    if len(accounts) == 0:
        await message.answer("У Вас пока нет счетов.", reply_markup=account_KB)    
    else:
        btns = {}
        for account in accounts:
            btns[account.name] = f"getaccountid_{account.id}"
        await message.answer("Ваши счета:", reply_markup=get_callback_btns(btns=btns))  
        await message.answer("Можете выбрать счет для изменения или удаления", reply_markup=account_KB)

# Обработает коллбэк со счетом для изменения или удаления
@user_account_router.callback_query(F.data.startswith("getaccountid_"))
async def change_account_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    account = await orm_get_account(session, account_id)
    await callback.answer()
    await callback.message.answer("Выбран счет:")
    account_line = "Название счета: "+account.name+", Тип счета: "+account.type+", Валюта счета: "+account.currency+", Лимит счета: "+str(account.limit)
    await callback.message.answer(account_line, reply_markup=get_callback_btns(
                                    btns={
                                        "Удалить": f"deleteac_{account.id}",
                                        "Изменить": f"changeac_{account.id}",
                                    })
                             )       

# Обработаем коллбэк удаления счета
@user_account_router.callback_query(F.data.startswith("deleteac_"))
async def delete_account_callback(callback: types.CallbackQuery, session: AsyncSession):
    account_id = callback.data.split("_")[-1]
    await orm_delete_account(session, int(account_id))
    await callback.answer("Счет удален")
    await callback.message.answer("Счет удален!")

# Обработаем коллбэк изменения счета
@user_account_router.callback_query(StateFilter(None),F.data.startswith("changeac_"))
async def change_account_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    account_id = callback.data.split("_")[-1]
    account_for_change = await orm_get_account(session, int(account_id))
    AddAccount.for_change=account_for_change
    await callback.answer()
    await callback.message.answer("Введите название счета:", reply_markup=types.ReplyKeyboardRemove()) 
    await state.set_state(AddAccount.name)

# Добавление нового счета или редактируем старый: вводим наименование
@user_account_router.message(StateFilter(None), F.text.lower() == "добавить счет")
async def new_account_cmd(message: types.Message, state: FSMContext):
    await message.answer("Введите название счета:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddAccount.name)

# Добавление нового счета или редактируем старый: проверяем наименование
# формируем инлайн-кнопки с типами счетов
@user_account_router.message(AddAccount.name, or_f(F.text, F.text=='.'))
async def add_account_name(message: types.Message, state: FSMContext, session: AsyncSession):
    # проверка длины наименования счета
    if message.text == '.':
        await state.update_data(name=AddAccount.for_change.name)
    else:
        if len(message.text) > 20:
            await message.answer("Название счета не должно превышать 20 символов. \n Введите заново")
            return
        await state.update_data(name=message.text)
    account_types = await orm_get_account_types(session, message.from_user.id)
    if len(account_types) == 0:
        await message.answer("У Вас пока нет типов счетов.", reply_markup=account_KB)    
    else:
        btns = {}
        for account_type in await orm_get_account_types(session, message.from_user.id):
            btns[account_type.name] = f"getaccounttypeid_{account_type.id}"
        await message.answer("Выберите тип счета:", reply_markup=get_callback_btns(btns=btns)) 
    await state.set_state(AddAccount.type_id)


# Добавление нового счета или редактируем старый: обрабатывает колбэк-квери с типом счата
# А также формируем инлайн-кнопки с валютами
@user_account_router.callback_query(AddAccount.type_id, F.data.startswith("getaccounttypeid_"))
async def change_account_type_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    account_type_id = int(callback.data.split("_")[-1])
    account_type = await orm_get_account_type(session, account_type_id)
    await callback.answer()
    await state.update_data(type_id=int(account_type_id))
    await callback.message.answer("Выбран тип счета: "+account_type.name)

    account_currencies = await orm_get_account_currencies(session, callback.from_user.id)
    if len(account_currencies) == 0:
        await callback.message.answer("У Вас пока нет валют.", reply_markup=account_KB)    
    else:
        btns = {}
        for account_currency in await orm_get_account_currencies(session, callback.from_user.id):
            btns[account_currency.name] = f"getaccountcurrencyid_{account_currency.id}"
        await callback.message.answer("Выберите валюту счета:", reply_markup=get_callback_btns(btns=btns)) 
    await state.set_state(AddAccount.currency_id)   

# Добавление нового счета или редактируем старый: обрабатывает колбэк-квери с валютами
@user_account_router.callback_query(AddAccount.currency_id, F.data.startswith("getaccountcurrencyid_"))
async def change_account_type_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    account_currency_id = int(callback.data.split("_")[-1])
    account_currency = await orm_get_account_currency(session, account_currency_id)
    await callback.answer()
    await state.update_data(currency_id=int(account_currency_id))
    await callback.message.answer("Выбрана валюта: "+account_currency.name)
    if AddAccount.for_change:
        await callback.message.answer("Лимит по счету составляет:"+ str(AddAccount.for_change.limit)+" Можете ввести новый лимит или  '.', чтобы оставить лимит без изменения.")
    else:
        await callback.message.answer("Можете указать лимит ежемесячного расхода по счету (вещественное число), или укажите 0.0:")
    await state.set_state(AddAccount.limit)

# Добавление нового счета или редактируем старый: добавляем лимит и записываем счет в базу
@user_account_router.message(AddAccount.limit, or_f(F.text, F.text=='.'))
async def add_limit(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == '.':
        if AddAccount.for_change:
            await state.update_data(limit=AddAccount.for_change.limit)
        else:
            await state.update_data(limit=0)
    else:
        try:
            limit=float(message.text)
            await state.update_data(limit=limit)
        except:
            await message.answer("Лимит должен быть введен цифрами, дробная часть отделяется точкой. \n Введите заново")
            return
    data = await state.get_data()
    if AddAccount.for_change:
        await message.answer("Счет изменен", reply_markup=account_KB)
        await orm_change_account(session, AddAccount.for_change.id, data)
    else:
        await message.answer("Счет добавлен", reply_markup=account_KB)
        await orm_add_account(session, message.from_user.id, data)
    AddAccount.for_change = None        
    await state.clear()

# Вернемся в начало меню счетов
@user_account_router.message(F.text.lower() == "назад к меню счетов")
async def accaunt_menu_cmd(message: types.Message, state: FSMContext,):
    await message.answer("Вернемся в меню счетов", reply_markup=account_KB)
    await state.clear()


