from aiogram import  F, types, Router
from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kbds.reply import main_KB, balance_KB, account_KB, directory_KB, expenses_KB, earnings_KB, transfer_KB 

from handlers.user_account_type import user_account_type_router
from handlers.user_account_currency import user_account_currency_router
from handlers.user_account import account_KB, user_account_router
from handlers.user_category import user_category_router
from handlers.user_place import user_place_router
from handlers.user_budget import user_budget_router
from handlers.user_balance import user_balance_router
from handlers.user_reports import user_reports_router

from database.models import Account, Account_currency, Account_currency_default, Account_default, Account_type, \
                            Account_type_default, Category, Category_default, Place, Place_default, User
from common.states import AddAccount, AddAccountCurrency, AddAccountType, AddBudget, Period

user_private_router = Router()
user_private_router.include_router(user_account_router)
user_account_router.include_router(user_account_type_router)
user_account_router.include_router(user_account_currency_router)
user_private_router.include_router(user_category_router)
user_private_router.include_router(user_place_router)
user_private_router.include_router(user_budget_router)
user_private_router.include_router(user_balance_router)
user_private_router.include_router(user_reports_router)

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    stmt = select(User).where(User.id==message.from_user.id)

    if len(list(await session.scalars(stmt))) == 0:
        obj = User(
            id = message.from_user.id,
            )
        session.add(obj)
        
        # Заполним справочники по умолчанию
        query = select(Account_type_default)
        for i in list(await session.scalars(query)):
            # print(i.id, i.name)
            obj = Account_type(
                name = i.name,
                user_id = message.from_user.id,
            )
            session.add(obj)

        query = select(Account_currency_default)
        for i in list(await session.scalars(query)):
            # print(i.id, i.name)
            obj = Account_currency(
                name = i.name,
                user_id = message.from_user.id,
                cod = i.cod,
            )
            session.add(obj)

        query = select(Account_default)
        for i in list(await session.scalars(query)):
            # print(i.id, i.name)
            obj = Account(
                name = i.name,
                user_id = message.from_user.id,
                type_id = i.type_id,
                currency_id = i.currency_id,
                limit = 0
            )
            session.add(obj)

        query = select(Category_default)
        for i in list(await session.scalars(query)):
            # print(i.id, i.name)
            obj = Category(
                user_id = message.from_user.id,
                category_type = i.category_type,
                name = i.name,
            )
            session.add(obj)

        query = select(Place_default)
        for i in list(await session.scalars(query)):
            # print(i.id, i.name)
            obj = Place(
                user_id = message.from_user.id,
                name = i.name,
            )
            session.add(obj)

    await session.commit()

    await message.answer("Привет, посмотрите менюшку внизу.", reply_markup=main_KB,)             

@user_private_router.message((F.text.lower() == 'справочники'))
async def sheta_cmd(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=directory_KB)

@user_private_router.message(F.text.lower() == "остатки")
async def оstatki_cmd(message: types.Message):
    await message.answer("Выберите действие:" , reply_markup=balance_KB)

@user_private_router.message(F.text.lower() == "переводы")
async def оstatki_cmd(message: types.Message):
    await message.answer("Выберите действие:" , reply_markup=transfer_KB)

@user_private_router.message(F.text.lower() == "доходы")
async def rashod_cmd(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=earnings_KB)

@user_private_router.message(F.text.lower() == "расходы")
async def rashod_cmd(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=expenses_KB)

## Типовые действия
@user_private_router.message(StateFilter('*'), Command("отмена"))
@user_private_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()
    if current_state is None:
        return
    
    if (current_state == "AddAccount") | \
       (current_state.split('.')[0].split(":")[0] == "AddAccountType") | \
       (current_state.split('.')[0].split(":")[0] == "AddAccountCurrency") \
        :
        kb = account_KB
    else:
        kb = main_KB
        
    await state.clear()
    await message.answer("Действия отменены", reply_markup=kb)

#Вернутся на шаг назад (на прошлое состояние)
@user_private_router.message(StateFilter('*'), Command("назад"))
@user_private_router.message(StateFilter('*'), F.text.casefold() == "назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:

    current_state = await state.get_state()

    if current_state == AddAccountType.name:
            await message.answer('Предидущего шага нет, или введите название типа счета или напишите "отмена"')
            return

    if current_state == AddAccountCurrency.name:
            await message.answer('Предидущего шага нет, или введите название валюты счета или напишите "отмена"')
            return

    if current_state == AddAccount.name:
        await message.answer('Предидущего шага нет, или введите название счета или напишите "отмена"')
        return

    if current_state == AddBudget.account_id:
        await message.answer('Предидущего шага нет, выберите счет  или напишите "отмена"')
        return

    if current_state == Period.from_date:
        await message.answer('Предидущего шага нет, выберите счет  или напишите "отмена"')
        return

    previous = None

    for step in AddAccountCurrency.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Ок, вы вернулись к прошлому шагу \n {AddAccountCurrency.texts[previous.state]}")
            return
        previous = step

    for step in AddAccount.__all_states__:
            if step.state == current_state:
                await state.set_state(previous)
                await message.answer(f"Ок, вы вернулись к прошлому шагу \n {AddAccount.texts[previous.state]}")
                return
            previous = step

    for step in AddBudget.__all_states__:
            if step.state == current_state:
                await state.set_state(previous)
                await message.answer(f"Ок, вы вернулись к прошлому шагу \n {AddBudget.texts[previous.state]}")
                return
            previous = step


# Вернемся в начало
@user_private_router.message(or_f(F.text.lower() == "в начало", F.text.lower() == "home"))
async def home_cmd(message: types.Message, state: FSMContext):
    await message.answer("Вернемся в начало", reply_markup=main_KB)
    await state.clear()



