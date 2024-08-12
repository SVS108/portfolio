import re

from aiogram import  F, types, Router
from aiogram.filters import or_f, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from common.states import AddBudget
from database.models import Operation
from database.orm_query import orm_get_account_balance, orm_add_transaction, orm_get_account, orm_get_account_limit, \
                               orm_get_accounts, orm_get_accounts_with_currencies, orm_get_categories, \
                               orm_get_categories_by_operation, orm_get_month_account_expenses, orm_get_places
from kbds.inline import get_callback_btns
from kbds.reply import balance_KB, earnings_KB, expenses_KB, transfer_KB

user_budget_router = Router()

sclonenie = {
    "остатк" : {
        "imenit" : "Остаток",
        "rodit" : "Остатка"
        },
    "перевод" : {
        "imenit" : "Перевод",
        "rodit" : "Перевода"
        },
    "доход" : {
        "imenit" : "Доход",
        "rodit" : "Дохода"
        },
    "расход" : {
        "imenit" : "Расход",
        "rodit" : "Расхода"
        }
    }

# Делаем проводки в базе данных - остатки, переводы, доходы, расходы
@user_budget_router.message(StateFilter(None), or_f(F.text.lower() == "добавить доходы",
                                                     F.text.lower() == "добавить расходы", 
                                                     F.text.lower() == "изменить остатки", 
                                                     F.text.lower() == "добавить переводы")
                            )
async def add_balance_cmd(message: types.Message, session: AsyncSession,  state: FSMContext):
    AddBudget.action = message.text.lower().split(" ")[-1][:-1] # ------------ 0
    accounts = await orm_get_accounts_with_currencies (session, message.from_user.id)
    if len(accounts) == 0:
        await message.answer("У Вас пока нет счетов.", reply_markup=types.ReplyKeyboardRemove())    
    else:
        btns = {}
        for account in accounts:
            btns[account.name+' ('+account.curr_cod+")"] = f"getacc_{account.id}"
        await message.answer("Выберите счет:", reply_markup=get_callback_btns(btns=btns)) 
    await state.set_state(AddBudget.account_id)    

@user_budget_router.callback_query(AddBudget.account_id, F.data.startswith("getacc_"))
async def get_balance_account_callback_cmd(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):

    account_id = int(callback.data.split("_")[-1])
    account = await orm_get_account(session, account_id)
    await callback.answer()
    await callback.message.answer("Выбран счет:")
    await state.update_data(account_id=account_id) # ------------- 1
    account_line = "Название счета: "+account.name+", Тип счета: "+account.type+", Валюта счета: "+account.currency+", Лимит счета: "+str(account.limit)
    await callback.message.answer(account_line)
    balance = await orm_get_account_balance(session, account.id)
    if not balance:
            balance = 0
    await callback.message.answer("Остаток по счету: " + str(round(balance, 2)))
 
    if AddBudget.action == "перевод":
        accounts = await orm_get_accounts(session, callback.from_user.id)
        btns = {}
        for acc in accounts:
            if acc.id != account.id:
                btns[acc.name] = f"getacctr_{acc.id}"
        await callback.message.answer("Выберите счет для перевода:", reply_markup=get_callback_btns(btns=btns))
        await state.set_state(AddBudget.transfer_account_id)
    elif AddBudget.action == "остатк":
        await callback.message.answer("Введите сумму " + sclonenie[AddBudget.action]["rodit"])   
        await callback.message.answer("Для уменьшения остатка введите отрицательную сумму")       
        await state.set_state(AddBudget.sum)
    else:
        if AddBudget.action == "доход":
            categories = await orm_get_categories_by_operation(session, callback.from_user.id, Operation.earnings)
        else: 
            #расход":
            categories = await orm_get_categories_by_operation(session, callback.from_user.id, Operation.expenses)
        if len(categories) == 0:
            await callback.message.answer("У Вас пока нет категорий. Введите в справочниках", reply_markup=types.ReplyKeyboardRemove())    
            return
        btns = {}
        for cat in categories:
            btns[cat.name] = f"getcat_{cat.id}"
        await callback.message.answer("Выберите категорию:", reply_markup=get_callback_btns(btns=btns))  

        await state.set_state(AddBudget.category_id)

@user_budget_router.callback_query(AddBudget.transfer_account_id, F.data.startswith("getacctr_"))
async def get_balance_account_callback_cmd(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    account_id = int(callback.data.split("_")[-1])
    account = await orm_get_account(session, account_id)
    await callback.answer()
    await callback.message.answer("Выбран счет для перевода:")
    account_line = "Название счета: "+account.name+", Тип счета: "+account.type+", Валюта счета: "+account.currency+", Лимит счета: "+str(account.limit)
    await callback.message.answer(account_line)
    await state.update_data(transfer_account_id=account_id) # ------------- 1.1
    await callback.message.answer("Введите сумму " + sclonenie[AddBudget.action]["rodit"])   
    await state.set_state(AddBudget.sum)

@user_budget_router.callback_query(AddBudget.category_id, F.data.startswith("getcat_"))
async def get_balance_category_callback_cmd(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    if (AddBudget.action == "доход") | (AddBudget.action == "расход") :
        await state.update_data(category_id=int(callback.data.split("_")[-1])) # ------------- 2
        if AddBudget.action == "расход":
            places = await orm_get_places(session, callback.from_user.id)
            if len(places) == 0:
                await callback.message.answer("У Вас пока нет мест.", reply_markup=types.ReplyKeyboardRemove())    
            else:
                btns = {}
                for place in places:
                    btns[place.name] = f"getpl_{place.id}"
                await callback.message.answer("Выберите место:", reply_markup=get_callback_btns(btns=btns))  
            await state.set_state(AddBudget.place_id)
        else:
            await callback.message.answer("Введите сумму " + sclonenie[AddBudget.action]["rodit"])   
            await state.set_state(AddBudget.sum)

@user_budget_router.callback_query(AddBudget.place_id, F.data.startswith("getpl_"))
async def get_balance_place_callback_cmd(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    if AddBudget.action == "расход":
        await state.update_data(place_id=int(callback.data.split("_")[-1])) # ------------- 3
    await callback.message.answer("Введите сумму " + sclonenie[AddBudget.action]["rodit"])   
    await state.set_state(AddBudget.sum)

@user_budget_router.message(AddBudget.sum)
async def get_balance_sum_cmd(message: types.message, session: AsyncSession, state: FSMContext):
    # try:
    sum_text = message.text.replace(",",".")
    sums_text = re.findall(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', sum_text)
    sums_dig = sum([float(s) for s in sums_text])
    if ((AddBudget.action == "доход") | (AddBudget.action == "расход")) & (sums_dig < 0) :
         await message.answer("Вы ввели сумму "+str(round(sums_dig,2))+". Сумма должна быть положительным числом. \n Введите заново")
         return
    data = await state.get_data()
    balance = await orm_get_account_balance(session, data['account_id'])
    limit = await orm_get_account_limit(session, data['account_id'])
    month_expenses = await orm_get_month_account_expenses(session, data['account_id'])
    if not balance:
        balance = 0
    if not limit:
        limit = 0
    if not month_expenses:
        month_expenses = 0

    users_categories = await orm_get_categories(session, message.from_user.id)

    if AddBudget.action == "остатк":
        if sums_dig >= 0:
            await state.update_data(category_id=users_categories[2].id)
        else:
            await state.update_data(category_id=users_categories[3].id)
            sums_dig=-sums_dig
            if sums_dig > balance:
                await message.answer("Сумма больше остатка. \n Введите заново")
                return  
        await state.update_data(place_id=1)
    if AddBudget.action == "перевод":
        users_categories = await orm_get_categories(session, message.from_user.id)
        await state.update_data(category_id=users_categories[1].id)

    if ((AddBudget.action == "расход")|(AddBudget.action == "перевод")) & (sums_dig > balance) :
        await message.answer("Сумма больше остатка. \n Введите заново")
        return
    
    if (AddBudget.action == "расход") & (month_expenses < limit) & (month_expenses + sums_dig > limit):
        await message.answer("Вы достигли лимита. Превышение составило: " + str(round(month_expenses + sums_dig - limit, 2))) 
    await state.update_data(sum=sums_dig) # ------------- 4
    await message.answer("Можете ввести комментарий, либо поставьте точку, чтобы оставить его пустым") 
    await state.set_state(AddBudget.comment)
    
@user_budget_router.message(AddBudget.comment)
async def balance_comment_cmd(message: types.Message, session: AsyncSession, state: FSMContext):
    if message.text == ".":
        comment = ""
    else:
        comment = message.text
    await state.update_data(comment=comment) # ------------- 5
    data = await state.get_data()
    
    if data['sum'] == 0:
        await message.answer("Сумма "+ sclonenie[AddBudget.action]['rodit'] +"нулевая.. Изменения не трубуются..", reply_markup=balance_KB)
    else:
        if AddBudget.action == "остатк":
            kb = balance_KB
            
        elif AddBudget.action == "перевод":
            kb = transfer_KB
            await state.update_data(place_id = 1)
            data = await state.get_data()
            await orm_add_transaction(session, user_id=message.from_user.id, data=data)
            users_categories = await orm_get_categories(session, message.from_user.id)
            await state.update_data(category_id=users_categories[0].id)
            await state.update_data(account_id = data['transfer_account_id'])
        elif AddBudget.action == "доход":
            kb = earnings_KB 
            await state.update_data(place_id = 1)
            data = await state.get_data()
        else:
            kb = expenses_KB
        data = await state.get_data()
        await orm_add_transaction(session, user_id=message.from_user.id, data=data)
        await message.answer(sclonenie[AddBudget.action]['imenit']+ " введен.", reply_markup=kb)
    await state.clear()
    AddBudget.action = None

