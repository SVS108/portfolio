from aiogram import  F, types, Router
from aiogram.filters import or_f, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from common.states import AddBudget
from database.models import Operation
from database.orm_query import orm_get_account_balance, orm_add_transaction, orm_get_account, \
                               orm_get_accounts, orm_get_accounts_with_currencies, orm_get_categories, \
                               orm_get_categories_by_operation, orm_get_last_account_operation, orm_get_places
from kbds.inline import get_callback_btns
from kbds.reply import balance_KB

user_balance_router = Router()

@user_balance_router.message(StateFilter(None), F.text.lower() == "посмотреть остатки")
async def balance_cmd(message: types.Message, session: AsyncSession):
    accounts = await orm_get_accounts_with_currencies(session, message.from_user.id)
    await message.answer("Остатки на счетах:")
    total = {}
    for account in accounts:
        balance = await orm_get_account_balance(session, account.id)
        last_date = await orm_get_last_account_operation(session, account.id)
        if not balance:
            balance = 0
        message_line = "Счет: <b>" + account.name + " ("+ account.type +") </b> Остаток: " + \
                        "<b>" + str(round(balance, 2)) + "</b> ("+account.cod+")" + \
                        " Последняя операция: "+ str(last_date[0].day) + "-" + str(last_date[0].month) + \
                        "-" + str(last_date[0].year)
        if account.cod in total:
            total[account.cod] = total[account.cod] + balance
        else:
            total[account.cod] = balance
        await message.answer(message_line, parse_mode='HTML')
    
    await message.answer("Итого:")
    for key, value in total.items():
        await message.answer(key + ": <b>"+str(round(total[key], 2))+"</b>", parse_mode='HTML')


@user_balance_router.message(StateFilter(None), or_f(F.text.lower() == "добавить доходы",
                                                     F.text.lower() == "добавить расходы", 
                                                     F.text.lower() == "изменить остатки")
                            )
async def change_balance_cmd(message: types.Message, state: FSMContext, session: AsyncSession):
    AddBudget.action = message.text.lower().split(" ")[-1][:-1] # ------------ 0
    accounts = await orm_get_accounts(session, message.from_user.id)
    if len(accounts) == 0:
        await message.answer("У Вас пока нет счетов.", reply_markup=types.ReplyKeyboardRemove())    
    else:
        btns = {}
        for account in accounts:
            btns[account.name] = f"getacc_{account.id}"
        await message.answer("Выберите счет:", reply_markup=get_callback_btns(btns=btns))  
    await state.set_state(AddBudget.account_id)


@user_balance_router.callback_query(AddBudget.account_id, F.data.startswith("getacc_"))
async def get_account_balance_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    account = await orm_get_account(session, account_id)
    await callback.answer()
    await callback.message.answer("Выбран счет:")
    account_line = "Название счета: "+account.name+", Тип счета: "+account.type+", Валюта счета: "+account.currency+", Лимит счета: "+str(account.limit)
    await callback.message.answer(account_line)
    balance = await orm_get_account_balance(session, account.id)
    if not balance:
            balance = 0
    await callback.message.answer("Остаток по счету: " + str(round(balance, 2)))
    await state.update_data(account_id=account_id) # ------------- 1
 
    await callback.message.answer("Выберите тип категории:", 
                            reply_markup=get_callback_btns(
                                btns={
                                    "Доходы": "earnings",
                                    "Расходы": "expenses",
                                })
                            )       
    await state.set_state(AddBudget.category_type)

@user_balance_router.callback_query(AddBudget.category_type, F.data.contains("earnings"))
async def get_earnings_balance_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    await state.update_data(category_type=Operation.earnings)  # ------------- 2.1
    await state.set_state(AddBudget.category_id)
    await callback.answer() 
    await callback.message.answer("Выбран тип категории: " + Operation.earnings.value, reply_markup=types.ReplyKeyboardRemove())

@user_balance_router.callback_query(AddBudget.category_type, F.data.contains("expenses"))
async def get_expenses_balance_callback(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    
    await state.update_data(category_type=Operation.expenses)  # ------------- 2.2
    await callback.answer()
    await callback.message.answer("Выбран тип категории: " + Operation.expenses.value, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddBudget.category_id)
  

@user_balance_router.message(AddBudget.category_id)
async def get_balance_category_id_cmd(message: types.Message, state: FSMContext, session: AsyncSession):
    if AddBudget.action == "перевод":
        ...
    elif AddBudget.action == "остатк":
        AddBudget.mes = "остатка:"
        if AddBudget.category_type == Operation.earnings:
            await state.update_data(category_id=3)
        else:
            await state.update_data(category_id=4)
    else:
        if AddBudget.action == "доходы":
            categories = await orm_get_categories_by_operation(session, message.from_user.id, Operation.earnings)
        else: 
            #AddBudget.action == "добавить расходы":
            categories = await orm_get_categories_by_operation(session, message.from_user.id, Operation.expenses)
        if len(categories) == 0:
            await message.answer("У Вас пока нет категорий. Введите в справочниках", reply_markup=types.ReplyKeyboardRemove())    
            return
        btns = {}
        for cat in categories:
            btns[cat.name] = f"getcat_{cat.id}"
        await message.answer("Выберите категорию:", reply_markup=get_callback_btns(btns=btns))  

    # await message.answer("Введите место: ")   
    await state.set_state(AddBudget.place)

@user_balance_router.callback_query(AddBudget.place, F.data.startswith("gecat_"))
async def get_place_cmd(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    if AddBudget.action == "добавить доходы" | AddBudget.action == "добавить расходы" :
        await state.update_data(category_id=int(callback.data.split("_")[-1]))
    places = await orm_get_places(session, callback.message.from_user.id)
    if len(places) == 0:
        await callback.message.answer("У Вас пока нет мест.", reply_markup=types.ReplyKeyboardRemove())    
    else:
        btns = {}
        for place in places:
            btns[place.name] = f"getpl_{place.id}"
        await callback.message.answer("Выберите место:", reply_markup=get_callback_btns(btns=btns))  
    await callback.message.answer("Введите сумму " + AddBudget.action +"a ")   
    await state.set_state(AddBudget.sum)


@user_balance_router.callback_query(AddBudget.sum, F.data.startswith("getpl_"))
async def balance_sum_cmd(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    try:
        sum=float(callback.message.text)
    except:
        await callback.answer("Сумма должна быть введена цифрами, дробная часть отделяется точкой. \n Введите заново")
        return
    data = await state.get_data()
    balance = await orm_get_account_balance(session, data['account_id'])
    if not balance:
            balance = 0
    if (data['category_type'] == Operation.expenses) & (sum > balance):
        await callback.message.answer("Сумма больше остатка. \n Введите заново")
        return
    await state.update_data(sum=sum)
    await callback.answer("Можете ввести комментарий, либо поставьте точку, чтобы оставить его пустым")
    await state.set_state(AddBudget.comment)
    
@user_balance_router.message(AddBudget.comment)
async def balance_comment_cmd(message: types.Message, session: AsyncSession, state: FSMContext):
    
    if message.text == ".":
        comment = ""
    else:
        comment = message.text
    await state.update_data(comment=comment)
    data = await state.get_data()
    if data['sum'] == 0:
        await message.answer("Сумма изменения нулевая.. Изменения не трубуются..", reply_markup=balance_KB)
    else:
        await message.answer("Остаток изменен", reply_markup=balance_KB)
        await orm_add_transaction(session, user_id=message.from_user.id, data=data)
    await state.clear()
    AddBudget.action = None
    AddBudget.mes = None